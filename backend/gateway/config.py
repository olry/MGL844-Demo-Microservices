# Configuration du gateway.
# Toutes les valeurs viennent du fichier .env à la racine du projet.
# Si une variable manque dans le .env, le gateway refuse de démarrer.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore" : on ignore les variables du .env qui ne concernent
    # pas le gateway (par exemple DB_URL appartient à hello-service).
    model_config = SettingsConfigDict(extra="ignore")

    # URL interne (dans le réseau Docker) du service hello.
    hello_service_url: str

    # URL interne (dans le réseau Docker) du service notification.
    notify_service_url: str


# On crée l'objet settings dès l'import du module.
# Si une variable manque, pydantic lève une erreur tout de suite
# et le gateway ne démarre pas (échec rapide, pas de valeur par défaut cachée).
settings = Settings()
