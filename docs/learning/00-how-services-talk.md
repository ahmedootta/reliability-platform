# 00 · How services talk to each other

Before any code: this project is a set of programs that must coordinate. The most useful mental model is that **every arrow in the architecture diagram is a choice** between a few communication styles. Learn the styles and the choices become obvious.

## The four styles

| Style | Shape | Caller waits? | Typical tech | Failure looks like |
|---|---|---|---|---|
| **Request/response (sync RPC)** | "do this, tell me the result" | Yes | REST/JSON, gRPC | timeout, error code |
| **Event / webhook (push)** | "this happened, FYI" | No, fire and forget | HTTP POST to a URL | delivery retried or lost |
| **Message queue (async work)** | "someone please do this later" | No | Redis/RabbitMQ + Celery | job sits in queue, retried |
| **Pull / scrape** | "I'll come and look at you" | n/a | Prometheus scraping `/metrics` | target `up == 0` |

Rule of thumb: **use sync when you need the answer to continue, async when you don't, and pull when the observed thing shouldn't have to know about the observer.**

## Every arrow in this project

| From → To | Style | Protocol | Why this choice |
|---|---|---|---|
| Locust / prober → orders-api | request/response | REST over HTTP/1.1 + JSON | Public-facing API: any client, browser-friendly, easy to debug with curl. |
| orders-api → payments | request/response | **gRPC** over HTTP/2 + protobuf | Internal call where both sides are ours: typed contract, compact binary, built-in deadlines and status codes. |
| orders-api → PostgreSQL | request/response | PostgreSQL wire protocol over TCP | The database dictates the protocol. |
| orders-api → Redis (cache) | request/response | RESP over TCP | Same: Redis dictates it. |
| Prometheus → services | **pull** | HTTP GET `/metrics` (text format) | Prometheus decides the cadence; a dead target is detected *because* the scrape fails (`up == 0`). Services need no knowledge of Prometheus. |
| Prometheus → Alertmanager | push (events) | HTTP | Alerts are events. |
| Alertmanager → remediator | **webhook** | HTTP POST + JSON | Alertmanager *only* speaks webhooks, so the receiver's protocol is dictated by the sender. A good reminder: protocol choice depends on who the client is. |
| remediator → Celery worker | **message queue** | Redis as broker | The webhook handler must answer fast (Alertmanager retries slow receivers). The slow, fallible work (restart, wait, verify) is handed off and can be retried independently. |
| Celery Beat → worker | message queue | Redis as broker | Beat is just a clock that enqueues jobs on a schedule. |
| worker → Docker | request/response | HTTP over a Unix socket (via a proxy) | The Docker daemon's API. |
| worker → LLM provider | request/response | HTTPS + JSON | An external API: slow, paid, fallible. Hence timeouts, budgets, fallbacks. |

## Why the same system uses REST *and* gRPC

REST/JSON optimises for **reach**: any language, curl, browsers, humans reading payloads. gRPC optimises for **internal efficiency and correctness**: a schema both sides compile, binary encoding, streaming, deadlines propagated across calls. You'd put REST at the edge and gRPC between your own services. Using gRPC where the client is a third party (like Alertmanager) would make no sense, which is exactly why that arrow is a webhook.

## Failure modes change with the style

This is what reliability engineering actually cares about:

- **Sync calls** couple availability: if payments is down, orders' `POST /orders` fails too. Mitigations: **timeouts/deadlines** (never wait forever), **retries with backoff** (only for idempotent calls), **circuit breakers**.
- **Queues** decouple availability but add **delay** and a new failure: a queue that grows without being drained. You monitor queue depth.
- **Webhooks** can be lost or duplicated, so receivers must be **idempotent** (our dedupe by open incident).
- **Scrapes** fail visibly (`up == 0`), which is a feature.

## Checkpoint (teach-back)

Answer in your own words, in `notes/00.md`:

1. Why is Alertmanager → remediator a webhook rather than gRPC?
2. Why doesn't the webhook handler restart the container itself?
3. If payments becomes slow, what happens to orders-api's latency, and which mechanism limits the damage?
4. Why does Prometheus pulling make `up == 0` possible, and what would pushing lose?
