"""Contract tests for proto/payments/v1/payments.proto.

Field NUMBERS are the wire contract: on the wire a field is identified by its
number, never its name. Renumbering or reusing a number silently corrupts data
between a new client and an old server. These tests freeze the numbers.
"""

import pytest

from payments.v1 import payments_pb2, payments_pb2_grpc


def test_message_round_trips_through_bytes():
    req = payments_pb2.ChargeRequest(
        order_id="o-1",
        amount=payments_pb2.Money(currency="USD", amount_minor=1999),
        payment_method_token="tok_visa",
        idempotency_key="key-123",
    )
    wire = req.SerializeToString()
    parsed = payments_pb2.ChargeRequest.FromString(wire)
    assert parsed == req
    assert parsed.amount.amount_minor == 1999


def test_wire_encoding_uses_field_numbers_not_names():
    # GetPaymentRequest{payment_id="p1"}: tag byte 0x0a = (field 1 << 3 | wire type 2),
    # then length 2, then the bytes "p1". No field name appears anywhere.
    wire = payments_pb2.GetPaymentRequest(payment_id="p1").SerializeToString()
    assert wire == b"\x0a\x02p1"


def test_default_values_cost_nothing_on_the_wire():
    assert payments_pb2.ChargeRequest().SerializeToString() == b""


@pytest.mark.parametrize(
    ("message", "field", "number"),
    [
        (payments_pb2.ChargeRequest, "order_id", 1),
        (payments_pb2.ChargeRequest, "amount", 2),
        (payments_pb2.ChargeRequest, "payment_method_token", 3),
        (payments_pb2.ChargeRequest, "idempotency_key", 4),
        (payments_pb2.ChargeResponse, "payment_id", 1),
        (payments_pb2.ChargeResponse, "status", 2),
        (payments_pb2.ChargeResponse, "decline_reason", 3),
        (payments_pb2.Money, "currency", 1),
        (payments_pb2.Money, "amount_minor", 2),
    ],
)
def test_field_numbers_are_frozen(message, field, number):
    assert message.DESCRIPTOR.fields_by_name[field].number == number


def test_enum_zero_value_means_unspecified():
    assert payments_pb2.PaymentStatus.Value("PAYMENT_STATUS_UNSPECIFIED") == 0
    assert payments_pb2.ChargeResponse().status == payments_pb2.PAYMENT_STATUS_UNSPECIFIED


def test_service_exposes_client_stub_and_server_base_class():
    # Stub = what orders-api calls. Servicer = what payments-service subclasses.
    assert hasattr(payments_pb2_grpc, "PaymentServiceStub")
    assert hasattr(payments_pb2_grpc, "PaymentServiceServicer")
    methods = {m.name for m in payments_pb2.DESCRIPTOR.services_by_name["PaymentService"].methods}
    assert methods == {"Charge", "GetPayment"}
