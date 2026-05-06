# Image de base : Python 3.11 version légère (slim).
FROM python:3.11-slim

# Dossier de travail à l'intérieur du conteneur.
WORKDIR /app

# On copie d'abord requirements.txt seul pour profiter du cache Docker :
# si la liste des dépendances ne change pas, pip ne réinstalle pas tout
# au prochain build.
COPY requirements.txt .

# Installation des dépendances Python listées dans requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le dossier app/ du notification-service dans le conteneur.
COPY services/notification-service/app ./app

# Force Python à afficher les logs tout de suite (sans tampon).
ENV PYTHONUNBUFFERED=1

# Port exposé par le conteneur (le service écoute sur 8002 à l'intérieur).
EXPOSE 8002

# Commande lancée quand le conteneur démarre :
# uvicorn est le serveur ASGI qui fait tourner FastAPI.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
