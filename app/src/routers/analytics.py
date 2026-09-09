from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.analytics import DetectionEvent
from app.src.repos.analytics import AnalyticsRepository
from app.src.schemas.analytics import (
    DetectionEventCreate,
    DetectionEventResponse,
    DetectionFilters,
)
from app.src.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(
    db: Annotated[Session, Depends(get_db)],
) -> AnalyticsService:
    """Inyección de dependencias para el servicio de analítica."""
    return AnalyticsService(AnalyticsRepository(db))


def _to_response(event: DetectionEvent) -> DetectionEventResponse:
    return DetectionEventResponse(
        camera_id=cast(int, event.camera_id),
        zone_name=cast(str, event.zone_name),
        people_count=cast(int, event.people_count),
        timestamp=cast(datetime, event.timestamp),
        status="received",
    )


@router.post(
    "/detections",
    response_model=DetectionEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_detection(
    event: DetectionEventCreate,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> DetectionEventResponse:
    """Recibe y persiste un evento de detección."""
    return _to_response(service.register_detection(event))


@router.get("/detections", response_model=list[DetectionEventResponse])
def get_detections(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    camera_id: Annotated[int | None, Query(ge=0)] = None,
    zone_name: Annotated[str | None, Query(min_length=1)] = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Sequence[DetectionEventResponse]:
    """Lista eventos con filtros opcionales y paginación."""
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start_date debe ser anterior o igual a end_date",
        )
    filters = DetectionFilters(
        camera_id=camera_id,
        zone_name=zone_name,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return [_to_response(event) for event in service.get_detections(filters)]
