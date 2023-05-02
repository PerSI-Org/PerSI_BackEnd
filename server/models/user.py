from odmantic import Model, ObjectId
from typing import Optional
from pydantic import BaseModel, Field


class User(Model):
    name: str
    email: str
    password: str


class UserCreate(BaseModel):
    name: str = Field(None, example="김지우")
    email: str = Field(None, example="example@goolge.com")
    password: str = Field(None, example="example1234!")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, example="김지우")
    email: Optional[str] = Field(None, example="example@goolge.com")
    password: Optional[str] = Field(None, example="example1234!")


class UserLogin(BaseModel):
    email: str
    password: str
