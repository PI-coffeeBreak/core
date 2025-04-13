import requests
import sys
import logging
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak import connection
from keycloak.exceptions import RoleNotFoundException

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

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/token", auto_error=False)


def get_current_user(force_auth: bool = True):
    def _get_current_user(token: str = Depends(oauth2_scheme)):
        try:
            if not token and not force_auth:
                return None

            if not token and force_auth:
                raise HTTPException(
                    status_code=401, detail="Not authenticated")

            try:
                token_info = keycloak_openid.decode_token(
                    token,
                    key=keycloak_openid.public_key(),
                    options={"verify_signature": True,
                             "verify_aud": True, "exp": True}
                )
                return token_info
            except Exception as decode_error:
                logger.warning(f"Failed to decode token: {str(decode_error)}")
                user_info = keycloak_openid.introspect(token)
                if not user_info.get("active"):
                    if force_auth:
                        raise HTTPException(
                            status_code=401, detail="Invalid token")
                    return None
                return user_info

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            if force_auth:
                raise HTTPException(status_code=401, detail="Invalid token")
            return None
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
        except RoleNotFoundException:
            logger.warning(f"Role '{role_name}' not found. Creating...")
            keycloak_admin.create_realm_role({"name": role_name})
            role = keycloak_admin.get_realm_role(role_name)
        except Exception as e:
            raise
        logger.info(f"Assigned role '{role_name}' to user '{user_id}'")

    except Exception as e:
        logger.error(f"Failed to assign role {role_name} to user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assign role: {str(e)}")