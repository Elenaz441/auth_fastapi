from fastapi import Depends
from fastapi_users.authentication import BearerTransport

from database import AsyncSession, get_async_session
from auth.backend_refresh import AuthenticationBackendRefresh
from auth.tranport import BearerTransportRefresh
from auth.jwt_blacklist_strategy import JWTBlacklistStrategy
from config import settings

bearer_transport = BearerTransport(tokenUrl=settings.auth.token_url)

SECRET = settings.auth.secret_key


bearer_transport_refresh = BearerTransportRefresh(tokenUrl=settings.auth.token_url)


def get_jwt_strategy(db: AsyncSession = Depends(get_async_session)) -> JWTBlacklistStrategy:
    return JWTBlacklistStrategy(
        secret=SECRET,
        lifetime_seconds=settings.auth.lifetime_seconds_access,
        db=db
    )


def get_refresh_jwt_strategy(db: AsyncSession = Depends(get_async_session)) -> JWTBlacklistStrategy:
    return JWTBlacklistStrategy(
        secret=SECRET,
        lifetime_seconds=settings.auth.lifetime_seconds_refresh,
        db=db
    )


auth_backend_refresh = AuthenticationBackendRefresh(
    name="jwt",
    transport=bearer_transport_refresh,
    get_strategy=get_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
)
