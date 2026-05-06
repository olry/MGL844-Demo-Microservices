# Routes liées aux utilisateurs (le "C" de MVC : Controller).
# Ce fichier reçoit les requêtes HTTP, appelle le modèle pour la base
# de données et renvoie une réponse formatée par les vues (Pydantic).

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import create_user, get_user, list_users
from app.views.user import UserCreate, UserGreeting, UserOut

# Toutes les routes de ce fichier commencent par /users.
router = APIRouter(prefix="/users", tags=["users"])


# POST /users : crée un nouvel utilisateur.
# 1. On enregistre l'utilisateur dans la base de données.
# 2. On publie un événement "user.created" sur NATS, pour que d'autres
#    services (par exemple notification-service) puissent réagir.
# 3. On renvoie l'utilisateur créé (id, nom, date de création).
@router.post("", response_model=UserOut, status_code=201)
async def create(
    payload: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    u = await create_user(db, payload.name)

    # On publie l'événement avec les infos minimales (id et nom).
    # NATS attend des bytes, donc on encode le JSON en utf-8.
    await request.app.state.nats.publish(
        "user.created",
        json.dumps({"id": u.id, "name": u.name}).encode(),
    )

    return UserOut.model_validate(u)


# GET /users : retourne la liste de tous les utilisateurs.
@router.get("", response_model=list[UserOut])
async def index(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    items = await list_users(db)
    return [UserOut.model_validate(u) for u in items]


# GET /users/{user_id} : retourne un utilisateur précis avec sa salutation.
# Si l'utilisateur n'existe pas, on retourne 404.
@router.get("/{user_id}", response_model=UserGreeting)
async def show(user_id: int, db: AsyncSession = Depends(get_db)) -> UserGreeting:
    u = await get_user(db, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="user not found")
    return UserGreeting(id=u.id, name=u.name, message=u.greet())
