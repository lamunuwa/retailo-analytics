from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CameraBase(BaseModel):
    """Define los campos comunes de una camara"""

    name: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo")
    description: str | None = Field(
        None, max_length=255, description="Descripcion opcional de la ubicacion o proposito"
    )
    source_type: Literal["demo_video", "webcam", "rtsp"] = Field(
        ..., description="Tipo de fuente de video permitida en el sistema"
    )
    is_active: bool = Field(default=True, description="Indica si la camara esta activa")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CameraCreate(CameraBase):
    """Valida la creacion de una camara"""


class CameraUpdate(BaseModel):
    """Valida la actualizacion de una camara"""

    name: str | None = Field(None, min_length=1, max_length=100, description="Nombre descriptivo")
    description: str | None = Field(None, max_length=255, description="Descripcion opcional")
    source_type: Literal["demo_video", "webcam", "rtsp"] | None = Field(
        None, description="Tipo de fuente de video"
    )
    is_active: bool | None = Field(None, description="Indica si la camara esta activa")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "CameraUpdate":
        """Valida que exista al menos un cambio"""
        if not self.model_fields_set:
            raise ValueError("Se debe proporcionar al menos un campo para actualizar")
        return self


class CameraRead(CameraBase):
    """Representa la respuesta de una camara"""

    id: int = Field(..., description="ID unico autogenerado en la base de datos")
    store_id: int = Field(..., description="ID de la tienda vinculada")
    created_at: datetime = Field(..., description="Fecha y hora de creacion del registro")

    model_config = ConfigDict(from_attributes=True)
