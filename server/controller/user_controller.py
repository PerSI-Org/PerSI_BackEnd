from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from server.services.users import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,
    authenticate_user
)
from server.models.user import (
    User,
    UserUpdate,
    UserLogin
)

router = APIRouter()


@router.post("/", response_description="Add new user", response_model=User)
async def create_user(user: User = Body(...)):
    user = jsonable_encoder(user)
    try:
        new_user = await add_user(user)
        return new_user
    except DuplicateKeyError:
        raise HTTPException(
            status_code=400, detail="This email already exists")


@router.post("/login", response_description="Login user", response_model=User)
async def login_user(user_login: UserLogin = Body(...)):
    authenticated_user = await authenticate_user(user_login)
    if authenticated_user:
        return authenticated_user
    raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/", response_description="List all users", response_model=List[User])
async def get_users():
    users = await retrieve_users()
    return users


@router.get("/{id}", response_description="Get a single user", response_model=User)
async def get_user(id: str):
    user = await retrieve_user(id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.put("/{id}", response_description="Update a user", response_model=User)
async def update_user_data(id: str, data: UserUpdate = Body(...)):
    data = {k: v for k, v in data.dict(
        exclude_unset=True).items() if v is not None}
    if len(data) >= 1:
        user = await retrieve_user(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        updated_user = await update_user(user, data)
        return updated_user
    raise HTTPException(status_code=400, detail="No fields to update")


@router.delete("/{id}", response_description="Delete a user")
async def delete_user_data(id: str):
    user = await retrieve_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user(user)
    return {"message": "User deleted successfully"}
