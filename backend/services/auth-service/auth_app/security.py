# Outils de securite : hachage de mot de passe + emission/verification JWT.
#
# - bcrypt (via passlib) pour les mots de passe : on ne stocke JAMAIS le
#   mot de passe en clair, on stocke son hash. bcrypt est lent par design,
#   ce qui rend les attaques par force brute couteuses.
# - JWT (PyJWT) pour les tokens : le serveur emet un token signe que le
#   client envoie a chaque requete (en-tete Authorization: Bearer <token>).
#   La signature garantit que le token n'a pas ete modifie.

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from auth_app.config import settings


# bcrypt avec parametres par defaut (assez fort pour un projet pedagogique).
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, username: str) -> str:
    # "sub" = subject : l'identite du proprietaire du token (norme JWT).
    # "exp" = expiration : date apres laquelle le token n'est plus valide.
    # "iat" = issued at  : date d'emission, utile pour les audits.
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_min)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    # Si la signature est invalide ou si le token est expire,
    # PyJWT leve une exception. On la laisse remonter pour que le
    # controller la transforme en 401.
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
