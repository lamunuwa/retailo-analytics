from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.repos.analytics import AnalyticsRepository
from app.src.schemas.analytics import DetectionEventCreate, DetectionEventResponse
from app.src.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(
    db: Annotated[Session, Depends(get_db)],
) -> AnalyticsService:
    """Inyección de dependencias para el servicio de analítica."""
    repo = AnalyticsRepository(db)
    return AnalyticsService(repo)


@router.post(
    "/detections",
    response_model=DetectionEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_detection(
    event: DetectionEventCreate,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> DetectionEventResponse:
    """Recibe las métricas de conteo de personas y las persiste."""
    db_event = service.register_detection(event)
    return DetectionEventResponse(
        camera_id=db_event.camera_id,  # type: ignore[arg-type]
        zone_name=db_event.zone_name,  # type: ignore[arg-type]
        people_count=db_event.people_count,  # type: ignore[arg-type]
        timestamp=db_event.timestamp,  # type: ignore[arg-type]
        status="received",
    )


@router.get("/detections", response_model=list[DetectionEventResponse])
def get_detections( #mambo mambo
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> Sequence[DetectionEventResponse]:
    """Lista todos los eventos de detección almacenados."""
    db_events = service.get_detections()
    return [
        DetectionEventResponse(
            camera_id=e.camera_id,  # type: ignore[arg-type]
            zone_name=e.zone_name,  # type: ignore[arg-type]
            people_count=e.people_count,  # type: ignore[arg-type]
            timestamp=e.timestamp,  # type: ignore[arg-type]
            status="received",
        )
        for e in db_events
    ]