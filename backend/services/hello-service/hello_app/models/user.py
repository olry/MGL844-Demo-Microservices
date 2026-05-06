# Modèle utilisateur (le "M" de MVC : Model).
# Ce fichier décrit la table "users" en base de données et propose
# des fonctions simples pour créer, lire et lister les utilisateurs.

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from hello_app.database import Base


# Représentation Python de la table SQL "users".
# Chaque attribut de la classe correspond à une colonne en base.
class User(Base):
    __tablename__ = "users"

    # id : clé primaire auto-incrémentée par la base.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # name : nom de l'utilisateur, max 255 caractères, obligatoire.
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # created_at : date de création, remplie automatiquement par la base.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Méthode utilitaire qui produit la phrase de salutation.
    def greet(self) -> str:
        return f"Bonjour {self.name} !"


# Crée un utilisateur et le sauvegarde dans la base.
# flush() écrit en base sans committer, refresh() recharge les valeurs
# générées par la base (id, created_at).
async def create_user(db: AsyncSession, name: str) -> User:
    u = User(name=name)
    db.add(u)
    await db.flush()
    await db.refresh(u)
    return u


# Récupère un utilisateur par son id, ou None s'il n'existe pas.
async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


# Retourne la liste de tous les utilisateurs, du plus récent au plus ancien.
async def list_users(db: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id.desc())
    result = await db.scalars(stmt)
    return list(result.all())
