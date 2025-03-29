from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas.user import User as UserSchema, UserCreate
from dependencies.auth import get_current_user, check_role
from services.user_service import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user,
    list_roles,
    list_role_users
)

router = APIRouter()

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/im/organizer")
async def im_organizer(current_user: dict = Depends(check_role(["organizer"]))):
    return current_user

@router.post("/", response_model=UserSchema, dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def create_user_endpoint(user_data: UserCreate):
    try:
        created_user = await create_user(user_data.model_dump())
        return created_user
    except HTTPException as e:
        raise e
    
@router.get("/roles", dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def list_roles_endpoint():
    try:
        roles = await list_roles()
        return roles
    except HTTPException as e:
        raise e
    
@router.get("/roles/users", dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def list_roles_endpoint():
    try:
        role_users = await list_role_users()
        return role_users
    except HTTPException as e:
        raise e


@router.get("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def get_user_endpoint(user_id: str):
    try:
        user = await get_user(user_id)
        return user
    except HTTPException as e:
        raise e

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def list_users_endpoint():
    try:
        users = await list_users()
        return users
    except HTTPException as e:
        raise e

@router.put("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def update_user_endpoint(user_id: str, user_data: UserCreate):
    try:
        updated_user = await update_user(user_id, user_data.model_dump())
        return updated_user
    except HTTPException as e:
        raise e

@router.delete("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_role(["admin", "manage_users"]))])
async def delete_user_endpoint(user_id: str):
    try:
        deleted_user = await delete_user(user_id)
        return deleted_user
    except HTTPException as e:
        raise e

