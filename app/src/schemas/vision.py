from datetime import datetime

from pydantic import BaseModel, Field


class ZoneMetric(BaseModel):
    zone_id: int = Field(..., description="ID de la zona evaluada")
    visits: int = Field(..., description="Número total de visitas en la zona")
    dwell_seconds: int = Field(..., description="Segundos totales de permanencia en la zona")
    traffic_share: float = Field(
        ..., description="Porcentaje del tráfico total que recibió esta zona"
    )


class VideoResult(BaseModel):
    processed_frames: int = Field(..., description="Total de frames procesados en la sesión")
    elapsed_seconds: int = Field(..., description="Segundos que duró el procesamiento")
    detected_people: int = Field(..., description="Total de personas únicas detectadas")
    started_at: datetime = Field(..., description="Fecha y hora de inicio de la sesión")
    finished_at: datetime = Field(..., description="Fecha y hora de finalización de la sesión")
    zone_metrics: list[ZoneMetric] = Field(..., description="Métricas agregadas divididas por zona")
