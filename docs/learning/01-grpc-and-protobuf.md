# 01 · gRPC and Protocol Buffers

Read after [00 · How services talk](00-how-services-talk.md). Here we build the one contract in the project: [`proto/payments/v1/payments.proto`](../../proto/payments/v1/payments.proto).

## 1. The problem a `.proto` file solves

With REST/JSON, the "contract" is usually a wiki page or an OpenAPI file that humans keep in sync with code. Client and server each hand-write their own request/response classes, and drift shows up at runtime.

gRPC flips it: **write the contract first, in a language-neutral file, and generate code from it.** Both sides compile the same file, so they cannot disagree about what a `ChargeRequest` looks like.

```
payments.proto ──protoc──►  Python  (orders-api, payments-service)
   (the contract)       ├─►  Go      (if a Go service joined)
                        └─►  Java / TypeScript / ...
```

Two things are bundled in the name:
- **Protocol Buffers (protobuf)**: the schema language *and* the compact binary encoding.
- **gRPC**: the RPC framework that sends protobuf messages over **HTTP/2** and gives you call types, deadlines, status codes, metadata and streaming.

## 2. Anatomy of our `.proto`

| Piece | In our file | Meaning |
|---|---|---|
| `syntax = "proto3"` | top | Language version. Always proto3 for new work. |
| `package payments.v1` | top | Namespace **and version**. When we break compatibility we publish `payments.v2` beside it. |
| `import` | `google/protobuf/timestamp.proto` | Reuse another proto. Google ships "well-known types" (Timestamp, Duration, ...). |
| `message` | `ChargeRequest`, `Money`, ... | A typed record. Becomes a class. |
| `enum` | `PaymentStatus` | Named constants. The first value **must be 0** and conventionally means "unspecified", so an unset field is never mistaken for a real state. |
| `service` | `PaymentService` | A set of callable methods: `rpc Charge(ChargeRequest) returns (ChargeResponse)`. Becomes a client stub and a server base class. |
| `= 1`, `= 2` ... | after each field | **Field numbers.** The most important thing in the file (next section). |

Design choices worth being able to explain:
- `Money` uses **integer minor units** (`1999` = 19.99). Floats can't represent decimal money exactly.
- `idempotency_key` on `Charge`: if orders-api retries after a timeout, payments must not charge twice. Reliability is designed into the contract.

## 3. Field numbers and what's on the wire

On the wire, a field is identified by its **number**, not its name. Real output from this repo for a `ChargeRequest` (34 bytes, versus 140 bytes for compact JSON of the same data):

```
0a 03 6f 2d 31                      field 1 (order_id), length 3, "o-1"
12 08                               field 2 (amount),   length 8, a nested Money:
   0a 03 55 53 44                      field 1 (currency),     "USD"
   10 cf 0f                            field 2 (amount_minor), varint 1999
1a 08 74 6f 6b 5f 76 69 73 61       field 3 (payment_method_token), "tok_visa"
22 07 6b 65 79 2d 31 32 33          field 4 (idempotency_key), "key-123"
```

The first byte of each field is `(field_number << 3) | wire_type`: `0x0a` = field 1, type 2 (length-delimited); `0x22` = field 4. No names appear anywhere, which is why it's small, and why **renaming a field is safe but renumbering one is a disaster**. Default values (empty string, 0) aren't sent at all.

[`tests/test_proto_contract.py`](../../tests/test_proto_contract.py) freezes these numbers so an accidental change fails CI.

## 4. Compiling: what `make proto` does

```bash
python -m grpc_tools.protoc -I proto \
    --python_out=gen --pyi_out=gen --grpc_python_out=gen \
    proto/payments/v1/payments.proto
```

| Part | Meaning |
|---|---|
| `python -m grpc_tools.protoc` | `protoc` (the protobuf compiler) packaged as a Python module, so you don't install a separate binary. It also bundles the well-known `.proto` files. |
| `-I proto` | **Import root.** Imports and output paths are resolved relative to this. |
| `--python_out=gen` | Emit `payments_pb2.py`: the **message classes** (`ChargeRequest`, `Money`, ...). |
| `--grpc_python_out=gen` | Emit `payments_pb2_grpc.py`: the **client stub** (`PaymentServiceStub`) and **server base class** (`PaymentServiceServicer`). |
| `--pyi_out=gen` | Emit `.pyi` type hints so your editor autocompletes. |

Result in `gen/payments/v1/`. Things worth knowing:

- **Layout matters.** The generated `_pb2_grpc.py` contains `from payments.v1 import payments_pb2`. That import only works if `gen/` is on `sys.path` and the folder structure mirrors the proto package. This is the classic "ModuleNotFoundError after compiling" trap, and why we use `-I proto` with the `payments/v1/` directory.
- **We don't commit `gen/`.** It's a build artifact. Generated code is tied to the installed protobuf runtime version, and committing it causes version-mismatch errors and noisy diffs. The Dockerfiles and CI will run the same compile step.
- **Same contract, other languages:** swap the flag, e.g. `--go_out`, `--java_out`, or use the `buf` tool with a `buf.gen.yaml` describing plugins. Nothing in the `.proto` changes. That's the point of language-neutral.

## 5. How the two sides use the generated code

You'll see this for real in branch 2; this is only the shape.

```python
# CLIENT (orders-api): a "stub" makes a remote call look like a function call
stub = PaymentServiceStub(grpc.insecure_channel("payments:50051"))
reply = stub.Charge(ChargeRequest(order_id=..., idempotency_key=...), timeout=0.5)

# SERVER (payments-service): subclass the generated base class, fill in the logic
class PaymentService(PaymentServiceServicer):
    def Charge(self, request, context):
        ...
        return ChargeResponse(payment_id=..., status=PAYMENT_STATUS_APPROVED)
```

Neither side writes any networking, serialization or routing code. That all lives in the generated stub and the gRPC runtime.

## 6. Evolving a contract without breaking clients

Old clients and new servers (and vice versa) coexist during every deploy, so contracts must evolve compatibly.

| Change | Safe? |
|---|---|
| Add a new field with a **new number** | ✅ Old readers ignore it. |
| Add a new `rpc` | ✅ |
| Rename a field | ✅ on the wire (⚠️ breaks JSON mapping and generated code users) |
| **Change a field's number** | ❌ Data silently lands in the wrong field. |
| **Reuse a deleted field's number** | ❌ Old data gets misread. Use `reserved 5;` and `reserved "old_name";` when deleting. |
| Change a field's type | ❌ (a few combinations are compatible; assume not) |
| Remove an `rpc` clients still call | ❌ |

Breaking change needed? Publish `payments.v2` alongside `v1`, migrate callers, retire `v1`. Tools like `buf breaking` detect incompatible edits in CI.

## 7. gRPC runtime concepts to carry into branch 2

- **Four call types:** unary (what we use), server streaming, client streaming, bidirectional.
- **HTTP/2** multiplexes many calls over one connection. Consequence for scaling: a plain TCP load balancer balances *connections*, not *calls*, so one backend may get all traffic. Fix with client-side load balancing or an L7 proxy such as Envoy. Relevant when you answer "scale to 100 services".
- **Status codes** replace HTTP status codes. The ones that matter for reliability:

  | gRPC code | ≈ HTTP | Retry? |
  |---|---|---|
  | `OK` | 200 | – |
  | `INVALID_ARGUMENT` | 400 | No: fix the request |
  | `NOT_FOUND` | 404 | No |
  | `RESOURCE_EXHAUSTED` | 429 | Back off |
  | `DEADLINE_EXCEEDED` | 504 | Only if idempotent |
  | `UNAVAILABLE` | 503 | Yes, with backoff |
  | `INTERNAL` | 500 | Usually no |

- **Deadlines:** a client sets "give up after 500 ms" and the framework enforces it and can propagate it downstream. A call with no deadline can hang forever and hold resources, so **every call gets a deadline**.
- **Metadata:** gRPC's equivalent of HTTP headers. We'll carry the `x-request-id` here so one user request can be traced across both services.
- **Interceptors:** gRPC's middleware. We'll use them to record metrics and logs for every call, the same job as the HTTP middleware.
- **Health checking protocol** (`grpc.health.v1`): the standard way to ask a gRPC server "are you serving?". Used for readiness.
- **Reflection + `grpcurl`:** `curl` for gRPC. Because the wire format is binary, you can't just `curl` it; reflection lets tools discover the schema from a running server.

## Run it

```bash
make test        # creates .venv, compiles the proto, runs the contract tests
ls gen/payments/v1/
```

Then **break it on purpose**: change `amount_minor = 2;` to `= 7;` in the `.proto`, run `make test`, and read the failure. That's the safety net that stops a number change reaching a deploy.

## Checkpoint (teach-back)

Answer in your own words in `notes/01.md`:

1. What two things does the `.proto` generate, and which side uses each?
2. Why is renaming a field safe but renumbering one dangerous?
3. Why is `gen/` not committed to git?
4. `orders-api` calls `Charge` and gets `DEADLINE_EXCEEDED`. Is it safe to retry? What in our contract makes that true?
5. Why does Alertmanager → remediator use a webhook instead of gRPC?
