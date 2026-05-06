# Schémas Pydantic (le "V" de MVC : View).
# Ils définissent la forme des données qui entrent et sortent du service
# par HTTP. Pydantic valide automatiquement chaque champ.

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Données attendues quand un client crée un utilisateur (POST /users).
# Le nom doit faire entre 1 et 255 caractères.
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


# Données renvoyées au client après création ou dans la liste.
# from_attributes=True : permet de construire ce schéma directement
# à partir d'un objet SQLAlchemy (UserOut.model_validate(u)).
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


# Données renvoyées par GET /users/{id}, avec la phrase de salutation.
class UserGreeting(BaseModel):
    id: int
    name: str
    message: str
