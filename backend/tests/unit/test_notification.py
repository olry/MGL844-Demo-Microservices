# Tests unitaires du notification-service.
# Aucun conteneur Docker requis : on utilise une base SQLite temporaire
# et on fabrique des messages NATS factices pour tester le handler.

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from notif_app.controllers import health, notification
from notif_app.database import Base, engine


# Fixture : prépare une mini application FastAPI propre pour chaque test.
# On efface puis recrée la table notifications avant chaque test.
@pytest_asyncio.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    test_app = FastAPI()
    test_app.include_router(health.router)
    test_app.include_router(notification.router)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as c:
        yield c


# La route /health doit répondre avec le statut et le nom du service.
@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "name": "notification-service"}


# GET /notifications doit renvoyer une liste vide quand la base est vide.
@pytest.mark.asyncio
async def test_list_notifications_empty(client):
    r = await client.get("/notifications")
    assert r.status_code == 200
    assert r.json() == []


# Test direct des fonctions du modèle, sans passer par HTTP.
@pytest.mark.asyncio
async def test_model_functions_direct():
    from notif_app.database import SessionLocal
    from notif_app.models.notification import create_notification, list_notifications

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        async with db.begin():
            n = await create_notification(db, "Bonjour Test !")
            assert n.id is not None
            assert n.message == "Bonjour Test !"

            items = await list_notifications(db)
            assert len(items) == 1
            assert items[0].message == "Bonjour Test !"


# Test du handler NATS : on simule un message "user.created" et on vérifie
# qu'une notification est bien stockée en base. Pas de vrai NATS ici,
# on construit juste un objet avec un attribut data (bytes JSON).
@pytest.mark.asyncio
async def test_handle_user_created_persists_message():
    from notif_app.database import SessionLocal
    from notif_app.main import handle_user_created
    from notif_app.models.notification import list_notifications

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    msg = SimpleNamespace(data=json.dumps({"id": 42, "name": "Alice"}).encode())
    await handle_user_created(msg)

    async with SessionLocal() as db:
        items = await list_notifications(db)
        assert len(items) == 1
        assert items[0].message == "Bonjour Alice ! (id=42)"


# Test du lifespan : démarrage et arrêt sans vrai serveur NATS.
@pytest.mark.asyncio
async def test_lifespan_starts_and_stops():
    from notif_app.main import lifespan

    fake_nc = AsyncMock()
    test_app = FastAPI()

    with patch("notif_app.main.nats.connect", new=AsyncMock(return_value=fake_nc)):
        async with lifespan(test_app):
            assert test_app.state.nats is fake_nc
            fake_nc.subscribe.assert_awaited_once()
        fake_nc.drain.assert_awaited_once()
