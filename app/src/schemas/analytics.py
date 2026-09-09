from datetime import datetime

from pydantic import BaseModel, Field


class DetectionEventCreate(BaseModel):
    """Esquema para recibir los eventos de detección enviados por el script de visión."""
    camera_id: int = Field(..., description="ID único de la cámara que reporta")
    zone_name: str = Field(..., description="Nombre de la zona vigilada")
    people_count: int = Field(
        ...,
        ge=0,
        description="Cantidad de personas detectadas (no negativo)",
    )
    timestamp: datetime = Field(..., description="Marca de tiempo UTC del frame procesado")


class DetectionEventResponse(DetectionEventCreate):
    """Esquema de respuesta tras una ingesta exitosa."""
    status: str = Field(default="received", description="Estado de recepción del evento")