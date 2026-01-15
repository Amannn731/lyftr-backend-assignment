from fastapi import FastAPI, HTTPException
from app.models import init_db, get_connection
from app.config import WEBHOOK_SECRET

app = FastAPI()


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health/live")
def health_live():
    return {"status": "live"}


@app.get("/health/ready")
def health_ready():
    # Check WEBHOOK_SECRET
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="WEBHOOK_SECRET not set")

    # Check DB connectivity
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")

    return {"status": "ready"}
