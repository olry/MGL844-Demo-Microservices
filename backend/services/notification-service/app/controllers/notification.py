# Routes liées aux notifications.
# Ici on n'a qu'une seule route : lister toutes les notifications reçues.

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.notification import list_notifications
from app.views.notification import NotificationOut

# Toutes les routes de ce fichier commencent par /notifications.
router = APIRouter(prefix="/notifications", tags=["notifications"])


# GET /notifications : retourne la liste de toutes les notifications stockées.
# C'est utile pour vérifier que les événements NATS ont bien été reçus
# et traités par ce service.
@router.get("", response_model=list[NotificationOut])
async def index(db: AsyncSession = Depends(get_db)) -> list[NotificationOut]:
    items = await list_notifications(db)
    return [NotificationOut.model_validate(n) for n in items]
