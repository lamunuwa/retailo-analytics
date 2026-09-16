from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.repos.reporting import ReportingRepository
from app.src.schemas.reporting import AnalyticsSummary, Insight, TrafficMetric
from app.src.services.reporting import StoreAnalyticsService

router = APIRouter(tags=["Analytics"])


def get_store_analytics_service(
    session: Annotated[Session, Depends(get_db)],
) -> StoreAnalyticsService:
    """Construye el servicio de analitica"""
    return StoreAnalyticsService(ReportingRepository(session))


def _validate_request(
    service: StoreAnalyticsService,
    store_id: int,
    start_date: datetime | None,
    end_date: datetime | None,
) -> None:
    """Valida una consulta de analitica"""
    if not service.has_store(store_id):
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date no debe ser posterior a end_date",
        )


@router.get("/stores/{store_id}/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    store_id: int,
    service: Annotated[StoreAnalyticsService, Depends(get_store_analytics_service)],
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
) -> AnalyticsSummary:
    """Obtiene el resumen analitico de una tienda"""
    _validate_request(service, store_id, start_date, end_date)
    return service.summary(store_id, start_date, end_date)


@router.get("/stores/{store_id}/analytics/traffic", response_model=list[TrafficMetric])
def get_analytics_traffic(
    store_id: int,
    service: Annotated[StoreAnalyticsService, Depends(get_store_analytics_service)],
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
) -> list[TrafficMetric]:
    """Obtiene el trafico por zona de una tienda"""
    _validate_request(service, store_id, start_date, end_date)
    return service.traffic(store_id, start_date, end_date)


@router.get("/stores/{store_id}/analytics/insights", response_model=list[Insight])
def get_analytics_insights(
    store_id: int,
    service: Annotated[StoreAnalyticsService, Depends(get_store_analytics_service)],
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
) -> list[Insight]:
    """Obtiene los hallazgos de una tienda"""
    _validate_request(service, store_id, start_date, end_date)
    return service.insights(store_id, start_date, end_date)
