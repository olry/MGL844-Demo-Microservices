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

# On copie le code du gateway. Deux fichiers seulement : main.py et config.py.
COPY gateway/main.py gateway/config.py ./

# Force Python à afficher les logs tout de suite (sans tampon).
# Pratique pour voir les messages dans `docker compose logs`.
ENV PYTHONUNBUFFERED=1

# Port exposé par le conteneur (le gateway écoute sur 8000 à l'intérieur).
EXPOSE 8000

# Commande lancée quand le conteneur démarre :
# uvicorn est le serveur ASGI qui fait tourner FastAPI.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
