from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dependencies.auth import keycloak_openid
import logging

logger = logging.getLogger("coffeebreak.core")

router = APIRouter()

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token = keycloak_openid.token(form_data.username, form_data.password)
    logger.debug(f"Token: {token}")
    return token