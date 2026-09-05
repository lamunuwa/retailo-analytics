from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CameraBase(BaseModel):
    """
    Esquema base para las cámaras.
    Contiene los atributos comunes que se usarán en todas las operaciones (Crear, Leer, Actualizar).
    """
    name: str = Field(..., description="Nombre descriptivo de la cámara")
    description: str | None = Field(
        None, description="Descripción opcional de la ubicación o propósito"
    )
    
    # Literal restringe los valores permitidos estrictamente a estas tres opciones,
    # actuando como un validador de seguridad automático a nivel de API para evitar tipos extraños.
    source_type: Literal["demo_video", "webcam", "rtsp"] = Field(
        ..., description="Tipo de fuente de video permitida en el sistema"
    )
    is_active: bool = Field(default=True, description="Indica si la cámara está activa")
    #la indica para procesar seciones.


class CameraCreate(CameraBase):
    """
    Esquema para la creación (POST) de una cámara.
    """
    pass


class CameraUpdate(BaseModel):
    """
    Esquema para la actualización (PATCH) de una cámara.
    """
    name: str | None = Field(None, description="Nombre descriptivo de la cámara")
    description: str | None = Field(None, description="Descripción opcional")
    source_type: Literal["demo_video", "webcam", "rtsp"] | None = Field(
        None, description="Tipo de fuente de video"
    )
    is_active: bool | None = Field(None, description="Indica si la cámara está activa")


class CameraRead(CameraBase):
    """
    Esquema de salida o lectura (GET/Response).
    """
    id: int = Field(..., description="ID único autogenerado en la base de datos")
    store_id: int = Field(..., description="ID de la tienda (Store) a la que está vinculada")
    created_at: datetime = Field(..., description="Fecha y hora de creación del registro en BD")