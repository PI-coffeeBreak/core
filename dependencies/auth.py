from keycloak import connection
def custom_urljoin(a, b):
    # If 'a' ends with a slash and 'b' starts with one, remove one slash
    if a.endswith('/') and b.startswith('/'):
        return a + b[1:]
    # If 'a' doesn't end with a slash and 'b' starts with one, add a slash between them
    elif not a.endswith('/') and b.startswith('/'):
        return a + b
    # If 'a' ends with a slash and 'b' doesn't start with one, just concatenate
    elif a.endswith('/') and not b.startswith('/'):
        return a + b
    # If neither ends or starts with a slash, add one between them
    else:
        return a + '/' + b
connection.urljoin = custom_urljoin
from keycloak import KeycloakAdmin, KeycloakOpenID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import os
import logging
import sys
import requests

logger = logging.getLogger("coffeebreak.core")


# Keycloak configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

if not all([KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET]):
    logger.error("One or more Keycloak environment variables are not set. Exiting program.")
    raise sys.exit(1)

logger.info(f'Connecting with keycloak at: {KEYCLOAK_URL}')

# Initialize Keycloak OpenID (for authentication)
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=False
)

# Initialize Keycloak Admin (for group management, using the client credentials)
keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    realm_name=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=False
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verifica e retorna informações do usuário autenticado no Keycloak"""
    try:
        user_info = keycloak_openid.introspect(token)
        if not user_info.get("active"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_info
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_role(required_roles: list):
    """Verifica se o usuário possui pelo menos um dos papéis necessários"""
    def role_verifier(user_info: dict = Depends(get_current_user)):
        user_roles = user_info.get("realm_access", {}).get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Access denied")
        return user_info
    return role_verifier
