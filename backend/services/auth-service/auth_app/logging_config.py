# Configuration des logs structures (format JSON).
# Chaque ligne de log est un objet JSON contenant : horodatage, niveau,
# nom du service, message, et tout champ "extra" passe par l'appelant.
#
# Pourquoi du JSON ?
# - Lisible par machine : un outil d'aggregation (Loki, ELK, CloudWatch)
#   peut filtrer/chercher par champ sans avoir a parser une regex.
# - Discipline d'equipe : tous les services emettent le meme format.

import json
import logging
import sys
from datetime import datetime, timezone


SERVICE_NAME = "auth-service"


class JsonFormatter(logging.Formatter):
    # Champs "techniques" du LogRecord qu'on ne veut pas dupliquer dans le JSON.
    _RESERVED = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "message", "module",
        "msecs", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Tout argument passe via logger.info("...", extra={"key": value})
        # apparait comme un champ JSON de haut niveau.
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # uvicorn cree ses propres loggers : on les force a passer par notre handler.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
