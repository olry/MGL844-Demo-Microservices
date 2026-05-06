# Point d'entrée du hello-service.
# Ce fichier crée l'application FastAPI, ouvre la base de données,
# se connecte à NATS et branche les routes (les controllers).

from contextlib import asynccontextmanager

import nats
from fastapi import FastAPI

from app.config import settings
from app.controllers import health, user
from app.database import Base, engine
# On importe le module User pour que SQLAlchemy connaisse la table "users"
# avant que create_all() ne crée les tables au démarrage.
from app.models import user as _user_model


# Lifespan : code qui tourne au démarrage et à l'arrêt du service.
# 1. On crée les tables dans la base SQLite si elles n'existent pas.
# 2. On ouvre la connexion vers NATS et on la garde dans app.state
#    pour que les routes puissent publier des événements.
# 3. À l'arrêt, on ferme proprement NATS et la base de données.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    nc = await nats.connect(settings.nats_url)
    app.state.nats = nc
    try:
        yield
    finally:
        await nc.drain()
        await engine.dispose()


# Création de l'application FastAPI avec le lifespan ci-dessus.
app = FastAPI(title="hello-service", lifespan=lifespan)

# On branche les deux groupes de routes : santé (/health) et utilisateurs (/users).
app.include_router(health.router)
app.include_router(user.router)
