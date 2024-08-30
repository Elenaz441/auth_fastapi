from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import (
    Strategy,
)
from fastapi_users.authentication.transport import (
    Transport,
)
from fastapi_users.types import DependencyCallable


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
        return await self.transport.get_login_response(access_token=token, refresh_token=refresh_token)
