from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class DetectionEventCreate(BaseModel):
    """Esquema para eventos enviados por el servicio de visión."""

    camera_id: int = Field(..., description="ID único de la cámara que reporta")
    zone_name: str = Field(..., description="Nombre de la zona vigilada")
    people_count: int = Field(..., ge=0, description="Cantidad de personas detectadas")
    timestamp: datetime = Field(..., description="Marca de tiempo UTC del frame")


class DetectionEventResponse(DetectionEventCreate):
    """Esquema de respuesta tras una ingesta exitosa."""

    status: str = Field(default="received", description="Estado de recepción del evento")


class DetectionFilters(BaseModel):
    """Filtros y paginación del listado de detecciones."""

    camera_id: int | None = Field(default=None, description="Filtrar por cámara")
    zone_name: str | None = Field(default=None, description="Filtrar por zona")
    start_date: datetime | None = Field(default=None, description="Fecha inicial inclusiva")
    end_date: datetime | None = Field(default=None, description="Fecha final inclusiva")
    limit: int = Field(default=100, ge=1, le=1000, description="Máximo de resultados")
    offset: int = Field(default=0, ge=0, description="Número de resultados a omitir")

    @model_validator(mode="after")
    def validate_date_range(self) -> "DetectionFilters":
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError("start_date debe ser anterior o igual a end_date")
        return self
