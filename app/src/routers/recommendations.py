from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.recommendations import RecommendationModel
from app.src.repos.recommendations import (
    RecommendationRepository,
    RecommendationRepositoryProtocol,
)
from app.src.repos.reporting import ReportingRepository, ReportingRepositoryProtocol
from app.src.schemas.recommendations import (
    RecommendationRead,
    RecommendationStatus,
    RecommendationStatusUpdate,
)
from app.src.services.reporting import StoreAnalyticsService

router = APIRouter(tags=["Recommendations"])


@router.post(
    "/stores/{store_id}/recommendations/generate",
    response_model=list[RecommendationRead],
    status_code=status.HTTP_201_CREATED,
)
def generate_recommendations(
    store_id: int,
    session: Annotated[Session, Depends(get_db)],
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
) -> list[RecommendationModel]:
    """Genera recomendaciones para una tienda"""
    reporting: ReportingRepositoryProtocol = ReportingRepository(session)
    if reporting.get_store_by_id(store_id) is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date no debe ser posterior a end_date",
        )
    insights = StoreAnalyticsService(reporting).insights(store_id, start_date, end_date)
    recommendations: RecommendationRepositoryProtocol = RecommendationRepository(session)
    return recommendations.create(store_id, insights)


@router.get("/stores/{store_id}/recommendations", response_model=list[RecommendationRead])
def get_all_recommendations(
    store_id: int,
    session: Annotated[Session, Depends(get_db)],
    recommendation_status: Annotated[RecommendationStatus | None, Query(alias="status")] = None,
) -> list[RecommendationModel]:
    """Obtiene las recomendaciones de una tienda"""
    reporting: ReportingRepositoryProtocol = ReportingRepository(session)
    if reporting.get_store_by_id(store_id) is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    recommendations: RecommendationRepositoryProtocol = RecommendationRepository(session)
    return recommendations.get_all_by_store(store_id, recommendation_status)


@router.patch(
    "/recommendations/{recommendation_id}/status",
    response_model=RecommendationRead,
)
def update_recommendation_status(
    recommendation_id: int,
    payload: RecommendationStatusUpdate,
    session: Annotated[Session, Depends(get_db)],
) -> RecommendationModel:
    """Actualiza el estado de una recomendacion"""
    repo: RecommendationRepositoryProtocol = RecommendationRepository(session)
    recommendation = repo.get_by_id(recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recomendacion no encontrada")
    return repo.update(recommendation, payload.status)
