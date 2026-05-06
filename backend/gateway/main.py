# Le gateway est la porte d'entrée de l'application.
# Tous les clients HTTP envoient leurs requêtes ici (port 8000).
# Le gateway regarde le premier mot de l'URL (par exemple /hello/...)
# et transfère la requête au bon service interne dans le réseau Docker.

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from config import settings


# Table des services connus.
# La clé est le nom utilisé dans l'URL publique, la valeur est l'adresse
# interne du service dans le réseau Docker.
# Pour ajouter un nouveau service : ajouter une ligne ici et dans le .env.
ROUTES: dict[str, str] = {
    "hello": settings.hello_service_url,
    "notify": settings.notify_service_url,
}


# Ces en-têtes HTTP appartiennent à la connexion entre le gateway et le service.
# Il ne faut PAS les recopier vers le client, sinon le navigateur reçoit
# des en-têtes incohérents et la réponse casse.
_HOP_BY_HOP = {"content-encoding", "transfer-encoding", "content-length", "connection"}


# Lifespan : code qui tourne au démarrage et à l'arrêt du serveur.
# On crée ici un client HTTP partagé (httpx) que toutes les requêtes
# vont réutiliser pour parler aux services internes.
# À l'arrêt, on ferme proprement le client.
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(timeout=30.0)
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(title="gateway", lifespan=lifespan)

# CORS : autorise le frontend (servi sur un autre port que le gateway)
# à appeler les endpoints depuis le navigateur.
# Pour un projet pédagogique, on autorise toutes les origines.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Route de santé du gateway lui-même.
# Docker appelle cette route pour vérifier que le gateway tourne bien.
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "name": "gateway"}


# Route générique qui transfère TOUTES les requêtes vers le bon service.
# Exemples :
#   GET  /hello/users/1         vers hello-service        : GET  /users/1
#   POST /hello/users           vers hello-service        : POST /users
#   GET  /notify/notifications  vers notification-service : GET  /notifications
# Si le nom du service n'existe pas dans ROUTES, on retourne 404.
@app.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy(service: str, path: str, request: Request) -> Response:
    # On vérifie si le nom du service est connu dans notre table ROUTES.
    upstream = ROUTES.get(service)
    if upstream is None:
        return Response(status_code=404, content=f"unknown service: {service}")

    # On reconstruit l'URL complète vers le service interne.
    url = f"{upstream}/{path}"

    # On recopie les en-têtes du client, sauf "host" qui doit changer
    # (le service interne a un autre nom de domaine que le client).
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    # On lit le corps de la requête (utile pour POST, PUT, PATCH).
    body = await request.body()

    # On envoie la requête au service interne et on attend sa réponse.
    resp = await app.state.client.request(
        request.method, url, params=request.query_params, content=body, headers=headers,
    )

    # On filtre les en-têtes techniques de la réponse avant de la renvoyer.
    out_headers = {k: v for k, v in resp.headers.items() if k.lower() not in _HOP_BY_HOP}

    # On renvoie la réponse du service interne au client, telle quelle.
    return Response(content=resp.content, status_code=resp.status_code, headers=out_headers)
