from datetime import UTC, datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

SessionStatus = Literal["running", "completed", "failed"]


class SessionCreate(BaseModel):
    """Entrada para iniciar una sesión de procesamiento."""

    started_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp de inicio del procesamiento de video",
    )

    model_config = ConfigDict(extra="forbid")


class SessionUpdate(BaseModel):
    """Entrada para cerrar una sesión con un estado terminal."""

    status: Literal["completed", "failed"] = Field(
        ..., description="Estado final de la sesión"
    )
    finished_at: AwareDatetime = Field(
        ..., description="Timestamp de finalización del procesamiento"
    )

    model_config = ConfigDict(extra="forbid")


class SessionRead(BaseModel):
    """Representación del estado de una sesión de procesamiento."""

    id: int = Field(..., description="ID único de la sesión")
    camera_id: int = Field(..., description="ID de la cámara asociada")
    status: SessionStatus = Field(..., description="Estado actual de la sesión")
    started_at: AwareDatetime = Field(..., description="Timestamp de inicio del procesamiento")
    finished_at: AwareDatetime | None = Field(
        None, description="Timestamp de finalización (None si aún está en progreso)"
    )
    created_at: AwareDatetime = Field(..., description="Fecha de creación del registro en BD")

    model_config = ConfigDict(from_attributes=True)
