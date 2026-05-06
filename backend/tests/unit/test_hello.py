# Tests unitaires du hello-service.
# Ces tests utilisent une base SQLite temporaire et un client FastAPI
# en mémoire (via ASGITransport). Aucun conteneur Docker requis ici.

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.controllers import health, user
from app.database import Base, engine
from app.models import user as _user_model


# Fixture : prépare une mini application FastAPI propre pour chaque test.
# 1. On efface puis recrée toutes les tables (chaque test part de zéro).
# 2. On crée une app FastAPI minimale avec juste les routes utilisateurs.
# 3. On branche un faux client NATS (AsyncMock) sur app.state.nats : le
#    contrôleur appellera publish() dessus sans avoir besoin d'un vrai NATS.
# 4. On ouvre un client httpx qui parle directement à l'app en mémoire.
@pytest_asyncio.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    test_app = FastAPI()
    test_app.state.nats = AsyncMock()
    test_app.include_router(health.router)
    test_app.include_router(user.router)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as c:
        yield c


# La route /health doit répondre avec le statut et le nom du service.
@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "name": "hello-service"}


# POST /users doit créer l'utilisateur et renvoyer son id et son nom.
@pytest.mark.asyncio
async def test_create_user(client):
    r = await client.post("/users", json={"name": "Alice"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Alice"
    assert isinstance(body["id"], int)


# GET /users doit lister les utilisateurs du plus récent au plus ancien.
@pytest.mark.asyncio
async def test_list_users(client):
    await client.post("/users", json={"name": "Alice"})
    await client.post("/users", json={"name": "Bob"})

    r = await client.get("/users")
    assert r.status_code == 200
    names = [u["name"] for u in r.json()]
    assert names == ["Bob", "Alice"]


# GET /users/{id} doit renvoyer l'utilisateur avec la phrase "Bonjour ...".
@pytest.mark.asyncio
async def test_get_user_returns_bonjour(client):
    r = await client.post("/users", json={"name": "Alice"})
    uid = r.json()["id"]

    r = await client.get(f"/users/{uid}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == uid
    assert body["name"] == "Alice"
    assert body["message"] == "Bonjour Alice !"


# GET /users/{id} doit renvoyer 404 quand l'utilisateur n'existe pas.
@pytest.mark.asyncio
async def test_get_user_404(client):
    r = await client.get("/users/9999")
    assert r.status_code == 404


# Test du modèle User : la méthode greet() retourne la phrase attendue.
# Pas besoin de base de données ici, on teste juste la classe Python.
def test_user_model_greet():
    from app.models.user import User
    assert User(name="World").greet() == "Bonjour World !"


# Tests directs des fonctions du modèle, sans passer par HTTP.
# On teste create_user, get_user et list_users avec une vraie session SQLite.
@pytest.mark.asyncio
async def test_model_functions_direct():
    from app.database import SessionLocal
    from app.models.user import create_user, get_user, list_users

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        async with db.begin():
            u = await create_user(db, "Direct")
            assert u.id is not None
            assert u.name == "Direct"

            same = await get_user(db, u.id)
            assert same is not None
            assert same.id == u.id

            all_users = await list_users(db)
            assert len(all_users) == 1
            assert all_users[0].name == "Direct"


# Tests directs des fonctions du controller, sans passer par HTTP.
# On vérifie create (avec publish NATS), index, show et show 404.
@pytest.mark.asyncio
async def test_controller_functions_direct():
    from app.controllers.user import create, index, show
    from app.database import SessionLocal
    from app.views.user import UserCreate

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    fake_request = AsyncMock()
    fake_request.app.state.nats = AsyncMock()

    async with SessionLocal() as db:
        async with db.begin():
            payload = UserCreate(name="DirectCtl")
            created = await create(payload, fake_request, db)
            assert created.name == "DirectCtl"
            fake_request.app.state.nats.publish.assert_awaited_once()

            listed = await index(db)
            assert len(listed) == 1

            greeting = await show(created.id, db)
            assert greeting.message == "Bonjour DirectCtl !"

            with pytest.raises(HTTPException) as exc:
                await show(9999, db)
            assert exc.value.status_code == 404


# Test du lifespan : on simule un démarrage et un arrêt sans vrai serveur NATS.
# On mocke nats.connect pour qu'il retourne un faux client. Le lifespan doit :
# 1. créer les tables (ne pas planter sur la base déjà existante),
# 2. connecter NATS et stocker le client dans app.state.nats,
# 3. à la sortie, appeler drain() puis dispose().
@pytest.mark.asyncio
async def test_lifespan_starts_and_stops():
    from app.main import lifespan

    fake_nc = AsyncMock()
    test_app = FastAPI()

    with patch("app.main.nats.connect", new=AsyncMock(return_value=fake_nc)):
        async with lifespan(test_app):
            assert test_app.state.nats is fake_nc
        fake_nc.drain.assert_awaited_once()
