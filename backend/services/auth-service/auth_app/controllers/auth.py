# Routes d'authentification.
# - POST /register : creer un compte.
# - POST /login    : verifier les identifiants et emettre un JWT.
# - GET  /me       : retourner l'utilisateur courant a partir du JWT.

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.config import settings
from auth_app.database import get_db
from auth_app.models.user import create_user, get_by_username
from auth_app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from auth_app.views.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

# Logger nomme : permet de filtrer les logs par module en production.
logger = logging.getLogger("auth_app.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    existing = await get_by_username(db, payload.username)
    if existing is not None:
        # On log l'evenement metier (pas un secret), pas le mot de passe.
        logger.warning("register_conflict", extra={"username": payload.username})
        raise HTTPException(status_code=409, detail="username already taken")

    u = await create_user(db, payload.username, hash_password(payload.password))
    logger.info("user_registered", extra={"user_id": u.id, "username": u.username})
    return UserOut(id=u.id, username=u.username)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await get_by_username(db, payload.username)
    # Note : meme message d'erreur pour "user inconnu" et "mauvais mot de passe"
    # pour ne pas reveler quels comptes existent (attaque par enumeration).
    if user is None or not verify_password(payload.password, user.password_hash):
        logger.warning("login_failed", extra={"username": payload.username})
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_access_token(user_id=user.id, username=user.username)
    logger.info("login_success", extra={"user_id": user.id, "username": user.username})
    return TokenResponse(access_token=token, expires_in=settings.jwt_expires_min * 60)


# Dependance reutilisable : extrait et valide le JWT de l'en-tete Authorization.
# A copier dans les autres services qui veulent proteger leurs routes.
async def current_user(authorization: str | None = Header(default=None)) -> dict:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        return decode_access_token(token)
    except Exception:
        logger.warning("token_invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserOut)
async def me(claims: dict = Depends(current_user)) -> UserOut:
    return UserOut(id=int(claims["sub"]), username=claims["username"])
