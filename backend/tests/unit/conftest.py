# Configuration pytest pour les tests unitaires.
# Ce fichier est chargé automatiquement par pytest avant tous les tests
# de ce dossier. Il prépare l'environnement avant l'import du module app.

import os
import tempfile

# Settings() exige DB_URL et NATS_URL sans valeurs par défaut dans le code.
# On les définit ICI, AVANT que app.config ne soit importé par les tests,
# sinon pydantic refuse de charger les Settings.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ.setdefault("DB_URL", f"sqlite+aiosqlite:///{_tmp.name}")
os.environ.setdefault("NATS_URL", "nats://localhost:4222")
