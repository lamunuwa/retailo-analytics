import os
import time
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.src.core.db import get_db

router = APIRouter(tags=["Health"])

START_TIME = time.monotonic()
VERSION = os.getenv("APP_VERSION", "1.0.0")


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Annotated[Session, Depends(get_db)]) -> JSONResponse:
    """Verifica la disponibilidad de la API y la conexión a la base de datos."""
    try:
        started_at = time.perf_counter()
        db.execute(text("SELECT 1"))
        database = {
            "status": "healthy",
            "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
        }
        response_status = status.HTTP_200_OK
        service_status = "ok"
    except Exception:
        database = {"status": "unhealthy", "latency_ms": None}
        response_status = status.HTTP_503_SERVICE_UNAVAILABLE
        service_status = "degraded"

    return JSONResponse(
        content={
            "status": service_status,
            "version": VERSION,
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime_seconds": round(time.monotonic() - START_TIME, 2),
            "checks": {"database": database},
        },
        status_code=response_status,
    )
