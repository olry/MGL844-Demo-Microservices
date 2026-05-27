# Point d'entree du auth-service.
# Cree l'application FastAPI, configure les logs JSON et la base de donnees.

from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth_app.controllers import auth, health
from auth_app.database import Base, engine
from auth_app.logging_config import configure_logging


# Lifespan : code qui tourne au demarrage et a l'arret du service.
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="auth-service", lifespan=lifespan)

app.include_router(health.router)
app.include_router(auth.router)
