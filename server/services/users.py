from typing import List, Optional
from bson.objectid import ObjectId
from passlib.context import CryptContext
from fastapi import HTTPException
from odmantic import AIOEngine
from server.models.user import User, UserUpdate, UserLogin
from server.config import MONGO_DB_NAME, MONGO_DB_URL
from server.models import mongodb

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def add_user(user: User) -> User:
    try:
        password_hash = await get_password_hash(user["password"])
        user["password"] = password_hash
        new_user = User(**user)
        await mongodb.engine.save(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def authenticate_user(user: UserLogin) -> User:
    try:
        db_user = await mongodb.engine.find_one(User, User.email == user.email)
        if not db_user:
            raise HTTPException(
                status_code=400, detail="Incorrect email or password")
        if not await verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=400, detail="Incorrect email or password")
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def retrieve_user(id: str) -> User:
    try:
        user = await mongodb.engine.find_one(User, User.id == ObjectId(id))
        return user
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")


async def retrieve_users() -> List[User]:
    try:
        users = []
        async for user in mongodb.engine.find(User):
            users.append(user)
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def update_user(user: User, data: UserUpdate) -> User:
    try:
        for field, value in data.items():
            if value is not None:
                setattr(user, field, value)
        updated_user = await mongodb.engine.save(
            user
        )
        if updated_user:
            return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def delete_user(user: User):
    try:
        await mongodb.engine.delete(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
