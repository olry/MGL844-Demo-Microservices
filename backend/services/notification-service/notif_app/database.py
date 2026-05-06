# Gestion de la base de données pour notification-service.
# Chaque service a SA propre base de données : c'est un principe
# important en architecture microservices (data ownership).

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from notif_app.config import settings


# engine : connexion vers la base. Ici un fichier SQLite séparé
# de celui de hello-service.
engine = create_async_engine(settings.notify_db_url, echo=False, future=True)

# SessionLocal : usine à sessions, une par requête HTTP ou par message NATS.
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Classe de base pour les modèles ORM (Notification, etc.).
class Base(DeclarativeBase):
    pass


# Dépendance FastAPI : fournit une session de base par requête HTTP.
# La transaction est gérée automatiquement (commit à la sortie, rollback en cas d'erreur).
async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        async with session.begin():
            yield session
