from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import hmac
import hashlib
import time
import uuid

from app.config import WEBHOOK_SECRET
from app.models import init_db, get_connection
from app.storage import insert_message
from app.logging_utils import log_event

app = FastAPI()


@app.on_event("startup")
def startup_event():
    init_db()


# --------------------
# Models
# --------------------
class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from", regex=r"^\+\d+$")
    to: str = Field(..., regex=r"^\+\d+$")
    ts: str
    text: Optional[str] = Field(None, max_length=4096)


# --------------------
# Helpers
# --------------------
def verify_signature(body: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        return False

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


# --------------------
# Routes
# --------------------
@app.post("/webhook")
async def webhook(
    request: Request,
    x_signature: Optional[str] = Header(None),
):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    body = await request.body()

    # Signature check
    if not x_signature or not verify_signature(body, x_signature):
        log_event(
            level="ERROR",
            request_id=request_id,
            method="POST",
            path="/webhook",
            status=401,
            result="invalid_signature",
        )
        raise HTTPException(status_code=401, detail="invalid signature")

    # Payload validation
    try:
        payload = WebhookMessage.parse_raw(body)
    except Exception:
        log_event(
            level="ERROR",
            request_id=request_id,
            method="POST",
            path="/webhook",
            status=422,
            result="validation_error",
        )
        raise

    data = payload.dict(by_alias=True)

    inserted = insert_message(data)

    latency_ms = int((time.time() - start_time) * 1000)

    log_event(
        level="INFO",
        request_id=request_id,
        method="POST",
        path="/webhook",
        status=200,
        message_id=data["message_id"],
        dup=not inserted,
        result="created" if inserted else "duplicate",
        latency_ms=latency_ms,
    )

    return {"status": "ok"}


# --------------------
# Health
# --------------------
@app.get("/health/live")
def health_live():
    return {"status": "live"}


@app.get("/health/ready")
def health_ready():
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="WEBHOOK_SECRET not set")

    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")

    return {"status": "ready"}
