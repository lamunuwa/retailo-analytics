from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.src.schemas.reporting import InsightType

RecommendationStatus = Literal["pending", "accepted", "rejected"]


class RecommendationStatusUpdate(BaseModel):
    """Valida el estado de una recomendacion"""

    status: RecommendationStatus

    model_config = ConfigDict(extra="forbid")


class RecommendationRead(BaseModel):
    """Representa la respuesta de una recomendacion"""

    id: int
    store_id: int
    zone_id: int
    zone_name: str
    insight_type: InsightType
    message: str
    suggestion: str
    status: RecommendationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
