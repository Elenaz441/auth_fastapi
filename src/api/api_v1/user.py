from fastapi import APIRouter
from schemas import UserRead, UserUpdate
from models import User
from uuid import UUID
from fastapi_users import FastAPIUsers
from auth import (
    get_user_manager,
    auth_backend_refresh,
)


fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend_refresh])


router = APIRouter(tags=["User"])

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
