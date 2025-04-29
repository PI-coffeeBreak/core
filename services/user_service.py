from typing import List
from dependencies.auth import keycloak_admin, assign_role
from exceptions.user import (
    UserNotFoundError,
    UserListError,
    UserCreateError,
    UserUpdateError,
    UserDeleteError,
    UserRoleError
)
import asyncio

async def list_users() -> List[dict]:
    try:
        users = keycloak_admin.get_users()
        return users
    except Exception as e:
        raise UserListError(str(e))


async def list_roles() -> List:
    try:
        # Fetch all roles
        roles = keycloak_admin.get_realm_roles()

        # Filter roles with "cb-" prefix
        filtered_roles = [
            role for role in roles if role["name"].startswith("cb-")]

        return filtered_roles
    except Exception as e:
        raise UserListError(str(e))


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
        raise UserListError(str(e))


async def get_user(user_id: str) -> dict:
    try:
        user = keycloak_admin.get_user(user_id)
        return user
    except Exception as _:
        raise UserNotFoundError(user_id)


async def create_user(user_data: dict) -> dict:
    try:
        user_id = keycloak_admin.create_user(user_data)
        return keycloak_admin.get_user(user_id)
    except Exception as e:
        raise UserCreateError(str(e))


async def update_user(user_id: str, user_data: dict) -> dict:
    try:
        keycloak_admin.update_user(user_id, user_data)
        return keycloak_admin.get_user(user_id)
    except Exception as e:
        raise UserUpdateError(str(e))


async def delete_user(user_id: str) -> dict:
    try:
        user = keycloak_admin.get_user(user_id)
        keycloak_admin.delete_user(user_id)
        return user
    except Exception as e:
        raise UserDeleteError(str(e))


async def assign_role_to_user(user_id: str, role_name: str):
    try:
        await asyncio.to_thread(assign_role, user_id=user_id, role_name=role_name)
    except ValueError as ve:
        raise UserRoleError(str(ve))