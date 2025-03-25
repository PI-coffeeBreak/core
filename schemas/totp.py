from pydantic import BaseModel

class OTPRequest(BaseModel):
    otp: str
