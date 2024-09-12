from fastapi import Response, status

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import (
    Strategy,
)
from fastapi_users.authentication.transport import (
    Transport,
    TransportLogoutNotSupportedError
)
from fastapi_users.types import DependencyCallable
from redis import Redis
from config import settings


class AuthenticationBackendRefresh(AuthenticationBackend):
    def __init__(self, name: str, transport: Transport,
                 get_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
                 get_refresh_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
                 redis: Redis):
        super().__init__(name, transport, get_strategy)
        self.refresh_strategy = get_refresh_strategy()
        self.redis = redis

    async def login(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UP,
    ) -> Response:
        token = await strategy.write_token(user)
        refresh_token = await self.refresh_strategy.write_token(user)
        await self.redis.set(f"pair:{token}", refresh_token, ex=settings.auth.lifetime_seconds_refresh)
        return await self.transport.get_login_response(access_token=token, refresh_token=refresh_token)

    async def logout(
        self, strategy: Strategy[models.UP, models.ID], user: models.UP, token: str
    ) -> Response:

        refresh_token = await self.redis.get(f"pair:{token}")
        await self.redis.set(f"blacklist:{token}", token, ex=settings.auth.lifetime_seconds_access)
        await self.redis.set(f"blacklist:{refresh_token}", refresh_token, ex=settings.auth.lifetime_seconds_refresh)
        await self.redis.delete(f"pair:{token}")

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
