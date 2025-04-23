from dependencies.auth import keycloak_admin, is_anonymous
from keycloak.exceptions import KeycloakError
from fastapi import HTTPException
import logging
logger = logging.getLogger("coffeebreak.core")


async def get_user_groups(user_id: str):
    """Retorna uma lista de todos os grupos aos quais um usuário pertence no Keycloak"""
    if is_anonymous(user_id):
        return []
    try:
        groups = keycloak_admin.get_user_groups(user_id)
        return groups
    except KeycloakError as e:
        logger.error(f"Failed to get user groups: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get user groups")


def create_group(group_name: str):
    """Cria um grupo no Keycloak usando `python-keycloak` com `fastapi-client`"""
    try:
        group_id = keycloak_admin.create_group({"name": group_name})
        return {"message": f"Group '{group_name}' created successfully", "group_id": group_id}
    except KeycloakError as e:
        logger.warning(f"Failed to create group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create group")


def add_client_to_group(client_id: str, group_name: str):
    """Adiciona um cliente a um grupo no Keycloak usando `python-keycloak`"""
    try:
        groups = keycloak_admin.get_groups()
        group = next((g for g in groups if g["name"] == group_name), None)

        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group '{group_name}' not found")

        group_id = group["id"]

        keycloak_admin.group_user_add(client_id, group_id)
        return {"message": f"Client '{client_id}' added to group '{group_name}' successfully"}

    except KeycloakError as e:
        logger.error(f"Failed to add client to group: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to add client to group")


def get_users_in_group(group_name: str):
    """Retorna uma lista de todos os usuários em um grupo específico no Keycloak"""
    try:
        # Buscar o ID do grupo pelo nome
        logger.debug("Fetching group ID: %s", group_name)
        groups = keycloak_admin.get_groups()
        group = next((g for g in groups if g["name"] == group_name), None)
        logger.debug("Group found: %s", group)

        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group '{group_name}' not found")

        group_id = group["id"]

        users = keycloak_admin.get_group_members(group_id)
        return users

    except KeycloakError as e:
        logger.error(f"Failed to get users in group: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get users in group")
