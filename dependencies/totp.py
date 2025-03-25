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
    hash = hmac_sha256.digest()
    # xor the first 16 bytes with the last 16 bytes
    hash = bytes([a ^ b for a, b in zip(hash[:16], hash[16:])])
    # base85 encode the hash
    signature = base64.b85encode(expiration + hash)
    return signature.decode()


def verify(data: str) -> bool:
    if len(data) < 25:
        return False
    
    logger.debug("Has the minimum length")
    signature = base64.b85decode(data[-25:].encode())
    expiration = int.from_bytes(signature[:4], byteorder='big')
    if expiration < time.time():
        return False
    
    logger.debug("Has the right time")
    msg = data[:-25]
    hmac_sha256 = hmac.new(k, digestmod=sha256)
    hmac_sha256.update(msg.encode())
    hmac_sha256.update(signature[:4])
    hash = hmac_sha256.digest()
    hash = bytes([a ^ b for a, b in zip(hash[:16], hash[16:])])
    return hash == signature[4:]


def encode(data: str) -> str:
    return data + sign(data)


def decode(data: str) -> str:
    if verify(data):
        return data[:-25]
    return None


def generate_qr_code(data: str) -> StreamingResponse:
    signed_data = encode(data)
    logger.debug(f"QR code generated: {signed_data}")
    qr = qrcode.make(signed_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


async def get_totp_user(otp_request: OTPRequest):
    otp = otp_request.otp
    data = decode(otp)
    if not data:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"user_id": data}


if __name__ == "__main__":
    signed_msg = sign("Hello World")
    print(signed_msg)
    print(verify(signed_msg))
    signed_msg = signed_msg[:-1] + "A" # tamper with the message
    print(verify(signed_msg))
