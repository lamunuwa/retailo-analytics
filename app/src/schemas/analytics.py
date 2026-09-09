
from pydantic import AwareDatetime, BaseModel, Field


class DetectionEventBase(BaseModel):
    """Esquema base con los atributos comunes de un evento de detección."""

    camera_id: int = Field(..., description="ID de la cámara asociada")
    zone_name: str = Field(..., description="Nombre de la zona monitoreada")
    people_count: int = Field(..., ge=0, description="Cantidad de personas detectadas")
    timestamp: AwareDatetime = Field(..., description="Marca de tiempo UTC del frame procesado")


class DetectionEventCreate(DetectionEventBase):
    """Esquema para la creación e ingesta de un nuevo evento de detección."""

    pass


class DetectionEventResponse(DetectionEventBase):
    """Esquema para responder la representación de un evento registrado."""

    status: str = Field(default="received", description="Estado del procesamiento")

    class Config:
        from_attributes = True


class DetectionFilters(BaseModel):
    """Parámetros de consulta para filtrado y paginación de eventos."""

    camera_id: int | None = Field(default=None, description="Filtrar por cámara")
    zone_name: str | None = Field(default=None, description="Filtrar por zona")
    start_date: AwareDatetime | None = Field(default=None, description="Fecha inicial inclusiva")
    end_date: AwareDatetime | None = Field(default=None, description="Fecha final inclusiva")
    limit: int = Field(default=100, ge=1, le=1000, description="Máximo de resultados")
    offset: int = Field(default=0, ge=0, description="Número de resultados a omitir")