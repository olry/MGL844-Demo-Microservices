# Gestion de la base de données pour hello-service.
# On utilise SQLAlchemy 2.0 en mode asynchrone avec un fichier SQLite.

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from hello_app.config import settings


# engine : objet qui gère la connexion vers la base de données.
# echo=False : on n'affiche pas les requêtes SQL dans les logs.
# Mettre echo=True peut être utile pour comprendre ce que SQLAlchemy fait.
engine = create_async_engine(settings.db_url, echo=False, future=True)

# SessionLocal : usine à sessions. Chaque requête HTTP utilisera sa propre session.
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Classe de base pour tous les modèles ORM.
# Tous les modèles (User, etc.) hériteront de cette classe.
class Base(DeclarativeBase):
    pass


# Dépendance FastAPI : fournit une session de base par requête.
# La transaction est ouverte à l'entrée et committée à la sortie automatiquement.
# En cas d'erreur, la transaction est annulée (rollback).
async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        async with session.begin():
            yield session
