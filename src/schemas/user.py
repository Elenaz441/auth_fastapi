from uuid import UUID

from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[UUID]):
    phone: str = Field(pattern=r'^\+\d{1,15}$')
    name: str = Field(min_length=2, max_length=50)


class UserCreate(schemas.BaseUserCreate):
    phone: str = Field(pattern=r'^\+\d{1,15}$')
    name: str = Field(min_length=2, max_length=50)
    # password: str = Field(pattern=r"^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", min_length=8, max_length=64) TODO validate password
    # password: str = Field(pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", min_length=8, max_length=64)


class UserUpdate(schemas.BaseUserUpdate):
    phone: str = Field(pattern=r'^\+\d{1,15}$')
    name: str = Field(min_length=2, max_length=50)
