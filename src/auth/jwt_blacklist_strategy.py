from fastapi_users import models, exceptions
from fastapi_users.jwt import SecretType, decode_jwt
from fastapi_users.authentication import JWTStrategy
from typing import Optional, List
from database import AsyncSession
from .service import add_token_to_blacklist, is_in_blacklist

import jwt

from fastapi_users.manager import BaseUserManager


class JWTBlacklistStrategy(JWTStrategy):
    def __init__(
            self,
            secret: SecretType,
            lifetime_seconds: Optional[int],
            db: AsyncSession,
            token_audience: List[str] = ["fastapi-users:auth"],
            algorithm: str = "HS256",
            public_key: Optional[SecretType] = None,
    ):
        super().__init__(secret, lifetime_seconds, token_audience, algorithm, public_key)
        self.db = db

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        if token is None:
            return None

        if await is_in_blacklist(token, self.db):
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            user_id = data.get("sub")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def destroy_token(self, token: str, user: models.UP) -> None:
        await add_token_to_blacklist(token, self.db)
