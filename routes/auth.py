from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dependencies.auth import keycloak_openid
import keycloak
import logging

logger = logging.getLogger("coffeebreak.core")

router = APIRouter()

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        token = keycloak_openid.token(form_data.username, form_data.password)
    except keycloak.exceptions.KeycloakAuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    logger.debug(f"User {form_data.username} logged in")
    return token