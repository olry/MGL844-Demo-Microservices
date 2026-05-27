# Configuration du auth-service.
# Toutes les valeurs viennent du fichier .env a la racine du projet.
# Si une variable manque, le service refuse de demarrer (echec rapide).

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore" : on ignore les variables du .env qui ne concernent
    # pas ce service.
    model_config = SettingsConfigDict(extra="ignore")

    # Adresse de la base de donnees (fichier SQLite dans /data).
    auth_db_url: str

    # Cle secrete pour signer les JWT. A garder confidentielle.
    # En production, utiliser une cle aleatoire d'au moins 32 octets.
    jwt_secret: str

    # Algorithme de signature. HS256 = HMAC avec SHA-256 (symetrique, simple).
    jwt_algorithm: str = "HS256"

    # Duree de vie d'un token en minutes.
    jwt_expires_min: int = 60


# pydantic lit les variables d'environnement et leve une erreur
# tout de suite si une variable obligatoire manque.
settings = Settings()
