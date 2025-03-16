from keycloak import KeycloakOpenID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

keycloak_openid = KeycloakOpenID(server_url="https://keycloak:8443/auth/",
                                  client_id="fastapi-client",
                                  realm_name="coffeebreak",
                                  client_secret_key="...",
                                  verify=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://keycloak:8443/auth/realms/coffeebreak/protocol/openid-connect/token")

# Dependency to verify the token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user_info = keycloak_openid.decode_token(token, options={"verify_signature": False})
        return user_info
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")