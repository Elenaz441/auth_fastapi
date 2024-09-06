from fastapi import Response, status

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import (
    Strategy,
    StrategyDestroyNotSupportedError
)
from fastapi_users.authentication.transport import (
    Transport,
    TransportLogoutNotSupportedError
)
from fastapi_users.types import DependencyCallable

from config import settings


class AuthenticationBackendRefresh(AuthenticationBackend):
    def __init__(self, name: str, transport: Transport,
                 get_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
                 get_refresh_strategy: DependencyCallable[Strategy[models.UP, models.ID]]):
        super().__init__(name, transport, get_strategy)
        self.get_refresh_strategy = get_refresh_strategy

    async def login(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UP,
    ) -> Response:
        token = await strategy.write_token(user)
        refresh_strategy = self.get_refresh_strategy()
        refresh_token = await refresh_strategy.write_token(user)

        response = await self.transport.get_login_response(token=token)
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.auth.lifetime_seconds_refresh,
            secure=True,
            httponly=True,
            samesite="none"
        )
        return response

    async def logout(
        self, strategy: Strategy[models.UP, models.ID], user: models.UP, token: str
    ) -> Response:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        response.set_cookie(
            "refresh_token",
            "",
            secure=True,
            httponly=True,
            samesite="none"
        )
        return response
