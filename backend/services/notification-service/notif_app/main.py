# Point d'entrée du notification-service.
# Ce service écoute l'événement "user.created" sur NATS et stocke
# une notification dans sa propre base SQLite.
# Il expose aussi la route GET /notifications pour lister ce qu'il a reçu.

import json
from contextlib import asynccontextmanager

import nats
from fastapi import FastAPI

from notif_app.config import settings
from notif_app.controllers import health, notification
from notif_app.database import Base, SessionLocal, engine
from notif_app.models.notification import create_notification


# Fonction appelée par NATS à chaque message reçu sur "user.created".
# msg.data contient les bytes envoyés par hello-service (un JSON utf-8).
# Elle est isolée au niveau module pour pouvoir être testée en unitaire
# sans avoir besoin d'un vrai serveur NATS.
async def handle_user_created(msg) -> None:
    data = json.loads(msg.data)
    message = f"Bonjour {data['name']} ! (id={data['id']})"
    async with SessionLocal() as db, db.begin():
        await create_notification(db, message)


# Lifespan : code qui tourne au démarrage et à l'arrêt du service.
# 1. On crée la table "notifications" dans SQLite si elle n'existe pas.
# 2. On se connecte à NATS et on s'abonne au sujet "user.created".
# 3. À chaque message reçu, handle_user_created enregistre une ligne.
# 4. À l'arrêt, on ferme proprement NATS et la base.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    nc = await nats.connect(settings.nats_url)
    await nc.subscribe("user.created", cb=handle_user_created)
    app.state.nats = nc

    try:
        yield
    finally:
        await nc.drain()
        await engine.dispose()


# Création de l'application FastAPI avec le lifespan ci-dessus.
app = FastAPI(title="notification-service", lifespan=lifespan)

# On branche les routes : santé (/health) et notifications (/notifications).
app.include_router(health.router)
app.include_router(notification.router)
