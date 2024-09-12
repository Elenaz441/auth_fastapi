from fastapi_users.authentication import BearerTransport, JWTStrategy

from database import redis_session
from auth.backend_refresh import AuthenticationBackendRefresh
from auth.tranport import BearerTransportRefresh
from config import settings

bearer_transport = BearerTransport(tokenUrl=settings.auth.token_url)

SECRET = settings.auth.secret_key

bearer_transport_refresh = BearerTransportRefresh(tokenUrl=settings.auth.token_url)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=settings.auth.lifetime_seconds_access,
    )


def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=settings.auth.lifetime_seconds_refresh,
    )


auth_backend_refresh = AuthenticationBackendRefresh(
    name="jwt",
    transport=bearer_transport_refresh,
    get_strategy=get_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
    redis=redis_session
)
