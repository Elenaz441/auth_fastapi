from typing import Annotated
from uuid import UUID
import string
import random
from redis import Redis
from fastapi_users import FastAPIUsers
from fastapi import APIRouter, Depends, HTTPException, Body, Response
from fastapi_users.authentication import JWTStrategy
from sqlalchemy import select

from database import AsyncSession, get_async_session, get_redis_async_session
from models import User
from auth import (
    get_user_manager,
    auth_backend_refresh,
    get_refresh_jwt_strategy,
    get_jwt_strategy,
    UserManager,
    add_token_to_blacklist,
    is_in_blacklist
)
from schemas import UserRead, UserCreate, BearerRefreshResponse
from config import settings
from mail_sender import get_login_message, conf
from fastapi_mail import FastMail, MessageSchema, MessageType

from httpx_oauth.clients.google import GoogleOAuth2

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend_refresh])
current_active_user = fastapi_users.current_user(active=True)

SECRET = "SECRET"

google_oauth_client = GoogleOAuth2(
    str(settings.google.client_id),
    str(settings.google.client_secret),
)

router = APIRouter(tags=["Auth"])


router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_auth_router(auth_backend_refresh))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
# router.include_router(
#     fastapi_users.get_oauth_router(google_oauth_client, auth_backend_refresh, SECRET),
#     prefix="/google",
# )


# TODO валидацию имени и телефона при регистрации

@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@router.post(settings.api.v1.auth.refresh, response_model=BearerRefreshResponse)
async def refresh_token(
    strategy: Annotated[JWTStrategy, Depends(get_jwt_strategy)],
    refresh_strategy: Annotated[JWTStrategy, Depends(get_refresh_jwt_strategy)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    refresh_token: Annotated[str, Body(..., embed=True)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not provided.")

    user = await refresh_strategy.read_token(refresh_token, user_manager)
    if not user or await is_in_blacklist(refresh_token, db):
        raise HTTPException(status_code=401, detail="Refresh token expired.")

    await add_token_to_blacklist(refresh_token, db)

    return await auth_backend_refresh.login(strategy, user)


@router.post(settings.api.v1.auth.login_email)
async def login_email(
    email: Annotated[str, Body(..., embed=True)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    redis: Annotated[Redis, Depends(get_redis_async_session)]
):
    user = await db.scalar(select(User).where(email == User.email))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    code = ''.join(random.choices(string.digits, k=6)) # TODO убрать константы в настройки!
    await redis.set(name=email, value=code, ex=300)

    text = get_login_message(code)
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[user.email],
        body=text,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return Response(content="Message sent!", status_code=202)


@router.post(settings.api.v1.auth.login_email_code, response_model=BearerRefreshResponse)
async def login_email_code(
    email: Annotated[str, Body(..., embed=True)],
    code: Annotated[str, Body(..., embed=True)],
    strategy: Annotated[JWTStrategy, Depends(get_jwt_strategy)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    redis: Annotated[Redis, Depends(get_redis_async_session)]
):
    user = await db.scalar(select(User).where(email == User.email))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    if not await redis.exists(email):
        raise HTTPException(status_code=404, detail="Code not found.")

    redis_code = await redis.get(name=email)
    if redis_code != code:
        raise HTTPException(status_code=400, detail="Incorrect code!")
    await redis.delete(email)

    return await auth_backend_refresh.login(strategy, user)

