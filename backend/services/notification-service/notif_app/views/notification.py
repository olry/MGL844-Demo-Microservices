# Schéma Pydantic pour les notifications (le "V" de MVC : View).
# Définit la forme des données renvoyées par GET /notifications.

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Données renvoyées au client.
# from_attributes=True : permet de construire ce schéma directement
# à partir d'un objet SQLAlchemy (NotificationOut.model_validate(n)).
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    created_at: datetime
