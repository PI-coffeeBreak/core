from typing import List
from dependencies.auth import keycloak_admin
from fastapi import HTTPException

async def list_users() -> List[dict]:
    try:
        users = keycloak_admin.get_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")
    
async def list_roles() -> List:
    try:
        roles = keycloak_admin.get_realm_roles()
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list roles: {str(e)}")
    
async def list_role_users() -> dict:
    roles = await list_roles()
    role_users = {}
    try:
        for r in roles:
            role_name = r["name"]
            users = keycloak_admin.get_realm_role_members(role_name)
            role_users[role_name] = users
            
        return role_users

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list role users: {str(e)}")

async def get_user(user_id: str) -> dict:
    try:
        user = keycloak_admin.get_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

async def create_user(user_data: dict) -> dict:
    try:
        user_id = keycloak_admin.create_user(user_data)
        return keycloak_admin.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

async def update_user(user_id: str, user_data: dict) -> dict:
    try:
        keycloak_admin.update_user(user_id, user_data)
        return keycloak_admin.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

async def delete_user(user_id: str) -> dict:
    try:
        user = keycloak_admin.get_user(user_id)
        keycloak_admin.delete_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")