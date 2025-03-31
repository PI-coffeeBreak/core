import os
from hashlib import sha256
import hmac
import time
import base64
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import Depends, HTTPException
import logging
from schemas.totp import OTPRequest

logger = logging.getLogger("coffeebreak.core")

validity = 3600 # seconds (int)

k = os.urandom(32)


def sign(data: str) -> str:
    hmac_sha256 = hmac.new(k, digestmod=sha256)
    hmac_sha256.update(data.encode())
    t = int(time.time())
    expiration = t + validity
    expiration = expiration.to_bytes(4, byteorder='big')
    hmac_sha256.update(expiration)
    digest = hmac_sha256.digest()
    # xor the first 16 bytes with the last 16 bytes
    digest = bytes([a ^ b for a, b in zip(digest[:16], digest[16:])])
    # base85 encode the hash
    signature = base64.b85encode(expiration + digest)
    return signature.decode()


def is_valid_signature_length(data: str) -> bool:
    return len(data) >= 25

def is_signature_expired(expiration: int) -> bool:
    return expiration < time.time()

def verify(data: str, signature: str) -> bool:
    if not is_valid_signature_length(signature):
        return False

    decoded_signature = base64.b85decode(signature.encode())
    expiration = int.from_bytes(decoded_signature[:4], byteorder='big')
    if is_signature_expired(expiration):
        return False

    hmac_sha256 = hmac.new(k, digestmod=sha256)
    hmac_sha256.update(data.encode())
    hmac_sha256.update(decoded_signature[:4])
    digest = hmac_sha256.digest()
    digest = bytes([a ^ b for a, b in zip(digest[:16], digest[16:])])
    logger.debug("digest (hex): %s", digest.hex())
    logger.debug("signature (hex): %s", decoded_signature[4:].hex())
    return digest == decoded_signature[4:]

def encode(data: str) -> str:
    return data + sign(data)


from typing import Optional

def decode(data: str) -> Optional[str]:
    if verify(data[:-25], data[-25:]):
        return data[:-25]
    return None

def generate_qr_code_bytes(data: str) -> bytes:
    signed_data = encode(data)
    qr = qrcode.make(signed_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

def generate_qr_code(data: str) -> StreamingResponse:
    signed_data = encode(data)
    logger.debug(f"QR code generated: {signed_data}")
    qr_bytes = generate_qr_code_bytes(data)
    return StreamingResponse(BytesIO(qr_bytes), media_type="image/png")

async def get_totp_user(otp_request: OTPRequest):
    otp = otp_request.otp
    data = decode(otp)
    if not data:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"user_id": data}


if __name__ == "__main__":
    signed_msg = encode("Hello World")
    print(signed_msg)
    print(verify(signed_msg[:-25], signed_msg[-25:]))
    signed_msg = signed_msg[:-1] + "A"
    print(verify(signed_msg[:-25], signed_msg[-25:]))
