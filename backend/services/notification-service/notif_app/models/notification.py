# Modèle Notification (le "M" de MVC : Model).
# Décrit la table "notifications" en base et propose des fonctions
# simples pour créer et lister les notifications.

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from notif_app.database import Base


# Représentation Python de la table SQL "notifications".
class Notification(Base):
    __tablename__ = "notifications"

    # id : clé primaire auto-incrémentée par la base.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # message : texte de la notification (max 500 caractères).
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    # created_at : date de création, remplie automatiquement par la base.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


# Crée une notification avec un message et la sauvegarde dans la base.
async def create_notification(db: AsyncSession, message: str) -> Notification:
    n = Notification(message=message)
    db.add(n)
    await db.flush()
    await db.refresh(n)
    return n


# Retourne la liste de toutes les notifications, de la plus récente
# à la plus ancienne.
async def list_notifications(db: AsyncSession) -> list[Notification]:
    stmt = select(Notification).order_by(Notification.id.desc())
    result = await db.scalars(stmt)
    return list(result.all())
