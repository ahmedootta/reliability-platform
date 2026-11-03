VENV := .venv
PY   := $(VENV)/bin/python
PROTO_FILES := $(shell find proto -name '*.proto')

.PHONY: venv proto test clean

venv: $(VENV)/.stamp

$(VENV)/.stamp: tools/requirements-dev.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r tools/requirements-dev.txt
	touch $@

# Compile every .proto into Python:
#   *_pb2.py       message classes (ChargeRequest, Money, ...)
#   *_pb2_grpc.py  client stub + server base class (PaymentServiceStub, PaymentServiceServicer)
#   *_pb2.pyi      type hints for editors/mypy
proto: venv
	rm -rf gen && mkdir -p gen
	$(PY) -m grpc_tools.protoc -I proto \
		--python_out=gen --pyi_out=gen --grpc_python_out=gen \
		$(PROTO_FILES)

test: proto
	$(VENV)/bin/pytest -q

clean:
	rm -rf gen $(VENV)
