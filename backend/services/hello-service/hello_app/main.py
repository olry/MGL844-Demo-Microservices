# Point d'entrée du hello-service.
# Ce fichier crée l'application FastAPI, ouvre la base de données,
# se connecte à NATS et à Redis, puis branche les routes (les controllers).

import logging
from contextlib import asynccontextmanager

import nats
import redis.asyncio as redis
from fastapi import FastAPI

from hello_app.config import settings
from hello_app.controllers import health, user
from hello_app.database import Base, engine
# Note : la table "users" est connue de SQLAlchemy parce que le module
# hello_app.models.user est importe en chaine via hello_app.controllers.user.

# On affiche les logs en INFO pour voir les lignes cache_hit / cache_miss.
logging.basicConfig(level=logging.INFO)


# Lifespan : code qui tourne au démarrage et à l'arrêt du service.
# 1. On crée les tables dans la base SQLite si elles n'existent pas.
# 2. On ouvre la connexion vers NATS (publication d'événements) et vers
#    Redis (cache partagé), gardées dans app.state pour les routes.
# 3. À l'arrêt, on ferme proprement NATS, Redis et la base de données.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    nc = await nats.connect(settings.nats_url)
    app.state.nats = nc

    # decode_responses=True : Redis nous renvoie des str (pas des bytes),
    # plus simple a manipuler avec json.
    app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)

    try:
        yield
    finally:
        await nc.drain()
        await app.state.redis.aclose()
        await engine.dispose()


# Création de l'application FastAPI avec le lifespan ci-dessus.
app = FastAPI(title="hello-service", lifespan=lifespan)

# On branche les deux groupes de routes : santé (/health) et utilisateurs (/users).
app.include_router(health.router)
app.include_router(user.router)
