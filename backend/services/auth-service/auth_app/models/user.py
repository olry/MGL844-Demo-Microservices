# Modele utilisateur (table "auth_users").
# On ne stocke JAMAIS le mot de passe en clair : seul son hash bcrypt.

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from auth_app.database import Base


class AuthUser(Base):
    __tablename__ = "auth_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


async def get_by_username(db: AsyncSession, username: str) -> AuthUser | None:
    stmt = select(AuthUser).where(AuthUser.username == username)
    return await db.scalar(stmt)


async def create_user(db: AsyncSession, username: str, password_hash: str) -> AuthUser:
    u = AuthUser(username=username, password_hash=password_hash)
    db.add(u)
    await db.flush()
    await db.refresh(u)
    return u
