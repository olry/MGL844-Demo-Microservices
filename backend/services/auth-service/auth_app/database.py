# Gestion de la base de donnees pour auth-service.
# SQLAlchemy 2.0 en mode asynchrone avec un fichier SQLite.

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from auth_app.config import settings


engine = create_async_engine(settings.auth_db_url, echo=False, future=True)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


# Dependance FastAPI : fournit une session de base par requete.
async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        async with session.begin():
            yield session
