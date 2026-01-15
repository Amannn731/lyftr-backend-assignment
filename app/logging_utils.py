import json
import logging
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log.update(record.extra)

        return json.dumps(log)


def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]


def log_event(level="INFO", message="", **kwargs):
    logger = logging.getLogger("app")
    logger.log(
        getattr(logging, level),
        message,
        extra={"extra": kwargs},
    )
