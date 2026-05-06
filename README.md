# MGL844 : Lab Microservices

[![Publish images to GHCR](https://github.com/olry/MGL844-Demo-Microservices/actions/workflows/publish.yml/badge.svg)](https://github.com/olry/MGL844-Demo-Microservices/actions/workflows/publish.yml)

Projet de départ pour le cours. Il contient un *gateway*, deux services
exemples (`hello-service` qui publie un événement, `notification-service`
qui le consomme), [NATS](https://docs.nats.io/) (un broker de messages)
et une petite interface web pour tester les endpoints.

## Architecture

![Composants](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/olry/MGL844-Demo-Microservices/main/doc/component.puml)

Le frontend appelle le `gateway`, qui transfère vers `hello-service`
ou `notification-service` selon le préfixe d'URL.
`hello-service` publie l'événement `user.created` sur NATS,
`notification-service` y est abonné et stocke chaque message reçu.
Les autres diagrammes (cas d'usage, séquence, classes, déploiement)
sont dans `doc/`.

Technos : [FastAPI](https://fastapi.tiangolo.com/),
[SQLAlchemy 2.0 async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html),
[Pydantic](https://docs.pydantic.dev/),
[nats-py](https://nats-io.github.io/nats.py/),
[Docker Compose](https://docs.docker.com/compose/),
[pytest](https://docs.pytest.org/).


## Démarrage rapide

Une seule chose requise : **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** installé et lancé.

**Windows (PowerShell)**
```
copy .env.example .env
docker compose up -d --build
```

**macOS / Linux**
```
cp .env.example .env
docker compose up -d --build
```

Attendre 15 secondes, puis ouvrir **<http://localhost:3000>** dans le navigateur.

C'est tout. L'interface web permet de tester chaque endpoint.

Pour tout arrêter :
```
docker compose down
```
Pour tout arrêter ET vider les bases de données :
```
docker compose down -v
```


## Sans builder localement (option : tirer les images depuis GHCR)

Les images sont publiées automatiquement sur **GitHub Container Registry**
à chaque push sur `main`. Pour récupérer la dernière version sans builder :

```
docker compose pull
docker compose up -d
```

Images disponibles (toutes en `:latest` et `:sha-XXXXXXX`) :

* `ghcr.io/olry/mgl844-demo-microservices/gateway`
* `ghcr.io/olry/mgl844-demo-microservices/hello-service`
* `ghcr.io/olry/mgl844-demo-microservices/notification-service`
* `ghcr.io/olry/mgl844-demo-microservices/frontend`


## URLs utiles

| Service | URL |
|---------|-----|
| **Interface web** | **<http://localhost:3000>** |
| Gateway (API) | <http://localhost:8000> |
| hello-service direct | <http://localhost:8001> |
| notification-service direct | <http://localhost:8002> |
| Swagger UI (hello) | <http://localhost:8001/docs> |
| Swagger UI (notify) | <http://localhost:8002/docs> |
| NATS monitoring | <http://localhost:8222> |


## Tester les endpoints

Deux façons :

**Option A : interface web** sur <http://localhost:3000> (bouton par endpoint).

**Option B : Swagger UI** généré automatiquement par FastAPI pour chaque service.
Tu vois la liste des routes, tu cliques "Try it out", tu remplis le corps,
tu cliques "Execute".

| Service              | Swagger UI                          |
|----------------------|-------------------------------------|
| hello-service        | <http://localhost:8001/docs>        |
| notification-service | <http://localhost:8002/docs>        |

Parcours typique pour voir l'événement NATS en action :

1. Sur Swagger hello : `POST /users` avec `{"name": "Alice"}`. Réponse 201.
2. Sur Swagger notify : `GET /notifications`. La liste contient
   `Bonjour Alice ! (id=1)` (publié par hello sur NATS, consommé par notify).


## Lancer les tests

Créer un environnement Python local (une seule fois) :

**Windows**
```
py -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt
```

**macOS / Linux**
```
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
```

Les tests sont rangés sous `backend/tests/` :

* `backend/tests/unit/` : tests unitaires (aucun conteneur requis).
* `backend/tests/integration/` : tests d'intégration (les conteneurs doivent tourner, voir le démarrage rapide).

Tout lancer :
```
.venv\Scripts\python -m pytest backend -v
```
(macOS / Linux : `.venv/bin/python -m pytest backend -v`)

Pour ne lancer qu'un seul groupe : remplacer `backend` par `backend/tests/unit` ou `backend/tests/integration`.

Le rapport de couverture s'affiche automatiquement après les tests unitaires.


## Dépannage

| Erreur | Cause | Solution |
|--------|-------|----------|
| `error while interpolating ... must be set in .env` | pas de fichier `.env` | refaire `copy .env.example .env` (Windows) ou `cp .env.example .env` (macOS/Linux) |
| `Bind for 0.0.0.0:8000 failed` | port 8000 déjà pris | changer `GATEWAY_PORT` dans `.env` ET la constante `GATEWAY` dans `frontend/app.js` |
| Port 3000 déjà pris | autre app utilise 3000 | changer `FRONTEND_PORT` dans `.env` |
| `nats` reste `unhealthy` | port 4222 déjà pris | redémarrer Docker Desktop, vérifier qu'aucun autre NATS ne tourne |
| L'interface web n'affiche rien | conteneurs pas encore prêts | attendre 15 s, puis `docker compose ps` (tout doit être `healthy`) |
