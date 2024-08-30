from uuid import UUID, uuid4

import sqlalchemy as alchemy
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id: Mapped[UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid4)
    token: Mapped[str] = mapped_column(String(length=1024), unique=True, nullable=False)
