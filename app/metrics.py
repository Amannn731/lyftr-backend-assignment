from fastapi import APIRouter, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

webhook_requests_total = Counter(
    "webhook_requests_total",
    "Total webhook requests",
    ["result"]
)

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
