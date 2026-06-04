# Routes liées aux utilisateurs (le "C" de MVC : Controller).
# Ce fichier reçoit les requêtes HTTP, appelle le modèle pour la base
# de données et renvoie une réponse formatée par les vues (Pydantic).

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from hello_app.database import get_db
from hello_app.models.user import create_user, get_user, list_users
from hello_app.views.user import UserCreate, UserGreeting, UserOut

logger = logging.getLogger("hello_app.user")

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
#
# CACHE PARTAGÉ (Redis, séance 8) : comme la gateway tourne en plusieurs
# instances et que ce service peut lui aussi être mis à l'échelle, le cache
# ne peut PAS vivre en mémoire locale (chaque instance aurait le sien). On le
# met dans Redis, partagé par toutes les instances.
@router.get("/{user_id}", response_model=UserGreeting)
async def show(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserGreeting:
    cache = request.app.state.redis
    cle = f"user:{user_id}"

    # 1. On regarde d'abord dans le cache.
    cached = await cache.get(cle)
    if cached is not None:
        # Cache HIT : la donnée était déjà en cache, on NE touche PAS la base.
        logger.info("cache_hit key=%s", cle)
        return UserGreeting(**json.loads(cached))

    # 2. Cache MISS : première lecture, on va chercher en base.
    logger.info("cache_miss key=%s", cle)
    u = await get_user(db, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="user not found")

    greeting = UserGreeting(id=u.id, name=u.name, message=u.greet())

    # 3. On met en cache avec un TTL de 60 secondes (ex=60) : passé ce délai,
    #    la clé expire et la prochaine lecture repassera par la base.
    await cache.set(cle, greeting.model_dump_json(), ex=60)
    return greeting
