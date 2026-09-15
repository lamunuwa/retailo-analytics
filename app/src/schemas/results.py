from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class ZoneMetricCreate(BaseModel):
    """Valida las metricas de una zona"""

    zone_id: int = Field(gt=0)
    visits: int = Field(ge=0)
    dwell_seconds: float = Field(ge=0)
    traffic_share: float = Field(ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class VideoResultCreate(BaseModel):
    """Valida el resultado de una sesion de video"""

    processed_frames: int = Field(ge=0)
    elapsed_seconds: float = Field(ge=0)
    detected_people: int = Field(ge=0)
    started_at: AwareDatetime
    finished_at: AwareDatetime
    zone_metrics: list[ZoneMetricCreate]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_result(self) -> "VideoResultCreate":
        """Valida fechas zonas y porcentajes"""
        if self.finished_at < self.started_at:
            raise ValueError("finished_at debe ser posterior o igual a started_at")
        zone_ids = [metric.zone_id for metric in self.zone_metrics]
        if len(zone_ids) != len(set(zone_ids)):
            raise ValueError("zone_metrics no puede repetir zone_id")
        total_share = sum(metric.traffic_share for metric in self.zone_metrics)
        if total_share > 100.01:
            raise ValueError("La suma de traffic_share no puede superar 100")
        return self


class ZoneMetricRead(ZoneMetricCreate):
    """Representa las metricas almacenadas de una zona"""

    id: int

    model_config = ConfigDict(from_attributes=True)


class VideoResultRead(BaseModel):
    """Representa el resultado almacenado de una sesion"""

    id: int
    session_id: int
    processed_frames: int
    elapsed_seconds: float
    detected_people: int
    started_at: datetime
    finished_at: datetime
    created_at: datetime
    zone_metrics: list[ZoneMetricRead]

    model_config = ConfigDict(from_attributes=True)
