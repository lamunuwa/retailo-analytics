from typing import Literal

from pydantic import BaseModel

InsightType = Literal[
    "HIGH_TRAFFIC_LOW_SALES",
    "LOW_TRAFFIC_HIGH_SALES",
    "LOW_TRAFFIC_LOW_SALES",
    "HIGH_TRAFFIC_HIGH_SALES",
]


class TopZone(BaseModel):
    """Representa la zona con mayor trafico"""

    zone_id: int
    zone_name: str
    visits: int


class AnalyticsSummary(BaseModel):
    """Representa el resumen analitico de una tienda"""

    store_id: int
    total_sessions: int
    processed_frames: int
    detected_people: int
    total_visits: int
    total_dwell_seconds: float
    total_units_sold: int
    total_revenue: float
    top_zone: TopZone | None


class TrafficMetric(BaseModel):
    """Representa las metricas de trafico de una zona"""

    zone_id: int
    zone_name: str
    zone_type: str
    visits: int
    dwell_seconds: float
    traffic_share: float
    units_sold: int
    revenue: float
    sales_share: float


class Insight(BaseModel):
    """Representa un hallazgo operativo"""

    type: InsightType
    zone_id: int
    zone_name: str
    message: str
    suggestion: str
    traffic_share: float
    sales_share: float
