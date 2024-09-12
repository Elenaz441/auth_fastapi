from uuid import UUID

from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[UUID]):
    phone: str = Field(pattern=r'^\+\d{1,15}$')
    name: str = Field(min_length=2, max_length=32)


class UserCreate(schemas.BaseUserCreate):
    phone: str = Field(pattern=r'^\+\d{1,15}$')
    name: str = Field(min_length=2, max_length=32)


class UserUpdate(schemas.BaseUserUpdate):
    phone: str = Field(pattern=r'^\+\d{1,15}$')
    name: str = Field(min_length=2, max_length=32)
