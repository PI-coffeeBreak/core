import logging
import os
import traceback
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from keycloak import KeycloakAdmin, KeycloakOpenID, connection
from keycloak.exceptions import KeycloakError
from datetime import datetime, timedelta, UTC
from uuid import uuid4
from jose import jwt, JWTError
from fastapi import Request


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

logger = logging.getLogger("coffeebreak.core")


# Keycloak configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

if not all([KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET]):
    logger.error("One or more Keycloak environment variables are not set.")
    raise RuntimeError("Missing Keycloak environment variables")

logger.info(f'Connecting with keycloak at: {KEYCLOAK_URL}')

# Initialize Keycloak OpenID (for authentication)
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=os.getenv("ENVIRONMENT", "development") == "production"
)

# Initialize Keycloak Admin (for group management, using the client credentials)
keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    realm_name=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=os.getenv("ENVIRONMENT", "development") == "production"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/token", auto_error=False)


SECRET_KEY = os.getenv("ANON_JWT_SECRET", "dev-secret")
ALGORITHM = "HS256"
ANON_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30


def create_anonymous_token():
    logger.info("Creating anonymous token")
    to_encode = {
        "sub": f"anon-{str(uuid4())}",
        "type": "anonymous",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=ANON_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def is_anonymous(user_data: dict | str):
    if isinstance(user_data, str):
        return user_data.startswith("anon-")
    return user_data.get("type") == "anonymous"


def get_current_user(force_auth: bool = True):
    def _get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
        if not force_auth and not token:
            try:
                if request.cookies.get("anon_token"):
                    anon_token = request.cookies.get("anon_token")
                    guest_user = jwt.decode(
                        anon_token, SECRET_KEY, algorithms=[ALGORITHM])
                    request.state.generated_token = anon_token
                    return guest_user
                anon_token = create_anonymous_token()
                guest_user = jwt.decode(
                    anon_token, SECRET_KEY, algorithms=[ALGORITHM])
                request.state.generated_token = anon_token
                return guest_user
            except Exception as e:
                logger.error(f"Anonymous token creation error: {str(e)}")
                raise HTTPException(
                    status_code=401, detail="Authentication error")

        try:
            if not token:
                raise HTTPException(status_code=401, detail="No token provided")
            token_info = keycloak_openid.decode_token(
                token,
                key=keycloak_openid.public_key(),
                verify_signature=False,  # ou True se tiver certeza que está OK
                verify_aud=True,
                exp=True
            )
            token_info["type"] = "authenticated"
            return token_info
        except Exception as decode_error:
            logger.warning(f"Decode failed: {decode_error}")
            try:
                user_info = keycloak_openid.introspect(token)
                if user_info.get("active"):
                    user_info["type"] = "authenticated"
                    return user_info
            except Exception as introspect_error:
                logger.error(f"Introspect failed: {introspect_error}")
                
        raise HTTPException(status_code=401, detail="Authentication error")

    return _get_current_user


def check_role(required_roles: list):
    def role_verifier(user_info: dict = Depends(get_current_user())):
        user_roles = user_info.get("realm_access", {}).get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Access denied")
        return user_info
    return role_verifier


def assign_role(user_id: str, role_name: str):
    """
    Assign a realm-level role to a user in Keycloak.
    Creates the role if it doesn't exist.
    """
    try:
        try:
            role = keycloak_admin.get_realm_role(role_name)
        except Exception as e:
            if "Could not find role" in str(e):
                logger.warning(f"Role '{role_name}' not found. Creating...")
                keycloak_admin.create_realm_role({"name": role_name})
                role = keycloak_admin.get_realm_role(role_name)
            else:
                raise
        keycloak_admin.assign_realm_roles(user_id=user_id, roles=[role])
        logger.info(f"Assigned role '{role_name}' to user '{user_id}'")

    except KeycloakError as e:
        logger.error(
            f"Failed to assign role {role_name} to user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to assign role: {str(e)}")
