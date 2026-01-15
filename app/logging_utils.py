import json
from datetime import datetime


def log_event(level: str, **fields):
    log = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": level,
        **fields,
    }
    print(json.dumps(log))
