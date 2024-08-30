from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TokenBlacklist


async def add_token_to_blacklist(token: str,
                                 db: AsyncSession):
    stmt = insert(TokenBlacklist).values({'token': token})
    await db.execute(stmt)
    await db.commit()


async def is_in_blacklist(token: str, db: AsyncSession) -> bool:
    result = await db.scalar(select(TokenBlacklist).where(token == TokenBlacklist.token))
    return result is not None
