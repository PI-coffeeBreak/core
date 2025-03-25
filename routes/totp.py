from fastapi import APIRouter, HTTPException, Depends
from schemas.totp import OTPRequest
from dependencies.totp import generate_qr_code, get_totp_user
from dependencies.auth import get_current_user

router = APIRouter()

@router.get("/generate-totp")
async def generate_otp(user: dict = Depends(get_current_user)):
    return generate_qr_code(user['sub'])

@router.post("/verify-totp")
async def verify_otp(otp_request: OTPRequest, user: dict = Depends(get_totp_user)):
    return {"user_id": user["user_id"]}
