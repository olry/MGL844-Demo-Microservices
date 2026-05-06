# Configuration pytest pour les tests unitaires.
# Ce fichier est chargé automatiquement par pytest avant tous les tests
# de ce dossier. Il prépare l'environnement avant l'import des modules
# hello_app et notif_app.

import os
import tempfile

# Settings() exige DB_URL, NOTIFY_DB_URL et NATS_URL, sans valeurs par
# defaut dans le code des services. On les definit ICI, AVANT que les
# modules de config ne soient importes, sinon pydantic refuse de charger.
_tmp_hello = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_hello.close()
_tmp_notif = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_notif.close()

os.environ.setdefault("DB_URL", f"sqlite+aiosqlite:///{_tmp_hello.name}")
os.environ.setdefault("NOTIFY_DB_URL", f"sqlite+aiosqlite:///{_tmp_notif.name}")
os.environ.setdefault("NATS_URL", "nats://localhost:4222")
