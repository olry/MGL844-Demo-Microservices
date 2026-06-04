# Configuration du hello-service.
# Toutes les valeurs viennent du fichier .env à la racine du projet.
# Si une variable manque, le service refuse de démarrer (échec rapide).

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore" : on ignore les variables du .env qui ne concernent
    # pas ce service (par exemple NOTIFY_DB_URL appartient à notification-service).
    model_config = SettingsConfigDict(extra="ignore")

    # Adresse de la base de données (ici un fichier SQLite dans /data).
    db_url: str

    # Adresse du serveur NATS dans le réseau Docker.
    nats_url: str

    # Adresse de Redis (cache partagé entre instances, séance 8).
    redis_url: str


# pydantic lit les variables d'environnement et lève une erreur
# tout de suite si une variable obligatoire manque.
settings = Settings()
