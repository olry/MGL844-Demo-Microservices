# Route de santé du hello-service.
# Docker l'appelle pour vérifier que le service tourne bien.

from fastapi import APIRouter

router = APIRouter()


# GET /health : retourne le statut et le nom du service.
# Permet d'identifier rapidement quel service répond.
@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "name": "hello-service"}
