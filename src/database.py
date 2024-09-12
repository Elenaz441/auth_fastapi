from typing import AsyncGenerator, Optional

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.models import UP

from config import settings
from models import User, OAuthAccount
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func, or_
import redis
import redis.asyncio


class MySQLAlchemyUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_login(self, login: str) -> Optional[UP]:
        statement = select(self.user_table).where(or_(
            self.user_table.phone == login,
            func.lower(self.user_table.email) == func.lower(login),
            self.user_table.name == login
        ))
        return await self._get_user(statement)

    async def get_by_phone(self, phone: str) -> Optional[UP]:
        statement = select(self.user_table).where(self.user_table.phone == phone)
        return await self._get_user(statement)

    async def get_by_name(self, name: str) -> Optional[UP]:
        statement = select(self.user_table).where(self.user_table.name == name)
        return await self._get_user(statement)


engine = create_async_engine(str(settings.db.url))
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


redis_session = redis.asyncio.StrictRedis(host=settings.redis.host,
                                         port=settings.redis.port,
                                         password=settings.redis.password,
                                         decode_responses=True)


async def get_redis_async_session() -> AsyncGenerator[redis.Redis, None]:
    async with redis.asyncio.StrictRedis(host=settings.redis.host,
                                         port=settings.redis.port,
                                         password=settings.redis.password,
                                         decode_responses=True) as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield MySQLAlchemyUserDatabase(session, User, OAuthAccount)
