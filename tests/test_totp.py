import pytest
import time
import base64
from fastapi.responses import StreamingResponse
from dependencies.totp import (
    sign,
    verify,
    encode,
    decode,
    generate_qr_code_bytes,
    is_valid_signature_length,
    is_signature_expired,
)

def test_sign_and_verify():
    test_data = "TestMessage"
    signed_data = sign(test_data)
    signature = signed_data[-25:]
    assert verify(test_data, signature), "Verification failed for valid signed data"
    tampered_signature = signature[:-1] + "A"
    assert not verify(test_data, tampered_signature), "Verification passed for tampered signature"

def test_encode_and_decode():
    test_data = "TestMessage"
    encoded_data = encode(test_data)
    decoded_data = decode(encoded_data)
    assert decoded_data == test_data, "Decoded data does not match original"
    tampered_data = encoded_data[:-1] + "A"
    assert decode(tampered_data) is None, "Decode passed for tampered data"

def test_generate_qr_code_bytes():
    test_data = "TestMessage"
    qr_bytes = generate_qr_code_bytes(test_data)
    assert isinstance(qr_bytes, bytes), "QR code bytes generation failed"
    assert len(qr_bytes) > 0, "QR code bytes are empty"

def test_is_valid_signature_length():
    assert is_valid_signature_length("A" * 25), "Valid signature length failed"
    assert not is_valid_signature_length("A" * 24), "Invalid signature length passed"

def test_is_signature_expired():
    future_time = int(time.time()) + 100
    past_time = int(time.time()) - 100
    assert not is_signature_expired(future_time), "Future time marked as expired"
    assert is_signature_expired(past_time), "Past time marked as valid"

def test_generate_qr_code():
    from dependencies.totp import generate_qr_code
    test_data = "TestMessage"
    response = generate_qr_code(test_data)
    assert isinstance(response, StreamingResponse), "QR code response is not StreamingResponse"
