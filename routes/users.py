from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.user import User as UserSchema, UserCreate
from dependencies.auth import get_current_user, check_role, keycloak_admin
from services.user_service import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user,
    list_roles,
    list_role_users
)
from exceptions.user import UserError
import logging

logger = logging.getLogger("coffeebreak.core")

router = APIRouter()

# Define native Keycloak roles that should be filtered out
KEYCLOAK_NATIVE_ROLES = {
    "offline_access",
    "uma_authorization",
    "default-roles-coffeebreak"
}


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user())):
    return current_user

@router.get("/guest/me")
def me(
    user = Depends(get_current_user(force_auth=False)),
    request: Request = None
):
    token = getattr(request.state, "generated_token", None)
    return {
        "user": user,
        "generated_token": token  # só vai aparecer se foi gerado no backend
    }

@router.get("/im/organizer")
async def im_organizer(current_user: dict = Depends(check_role(["organizer"]))):
    return current_user


@router.post("/", response_model=UserSchema, dependencies=[Depends(check_role(["manage_users"]))])
async def create_user_endpoint(user_data: UserCreate):
    try:
        created_user = await create_user(user_data.model_dump())
        return created_user
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/batch/", response_model=List[UserSchema], dependencies=[Depends(check_role(["manage_users"]))])
async def create_users_batch(users_data: List[UserCreate]):
    created_users = []
    for user_data in users_data:
        try:
            created_user = await create_user(user_data.model_dump())
            created_users.append(created_user)
        except UserError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))
    return created_users


@router.get("/roles/", dependencies=[Depends(check_role(["manage_users"]))])
async def list_roles_endpoint():
    try:
        roles = await list_roles()
        return roles
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/roles/users/", dependencies=[Depends(check_role(["manage_users"]))])
async def list_roles_endpoint():
    try:
        role_users = await list_role_users()
        return role_users
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_role(["manage_users"]))])
async def get_user_endpoint(user_id: str):
    try:
        user = await get_user(user_id)
        return user
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/", response_model=List[UserSchema], dependencies=[Depends(check_role(["manage_users"]))])
async def list_users_endpoint():
    try:
        users = await list_users()
        return users
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.put("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_role(["manage_users"]))])
async def update_user_endpoint(user_id: str, user_data: UserCreate):
    try:
        updated_user = await update_user(user_id, user_data.model_dump())
        return updated_user
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.delete("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_role(["manage_users"]))])
async def delete_user_endpoint(user_id: str):
    try:
        deleted_user = await delete_user(user_id)
        return deleted_user
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/permissions/", response_model=Dict[str, List[str]], dependencies=[Depends(check_role(["manage_users"]))])
async def get_permissions():
    """
    Get all available permissions in the system, categorized as custom and native.
    Returns a dictionary with permissions list, excluding native Keycloak roles.
    """
    try:
        roles = keycloak_admin.get_realm_roles()

        permissions = []

        for role in roles:
            role_name = role['name']
            if role_name not in KEYCLOAK_NATIVE_ROLES and not role_name.startswith("cb-"):
                permissions.append(role_name)

        return {
            "permissions": permissions,
        }
    except Exception as e:
        logger.error(f"Error fetching permissions: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch permissions")
