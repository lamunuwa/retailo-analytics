from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ZoneType = Literal["product_area", "checkout", "entrance_exit", "fridges", "other"]


class Point(BaseModel):
    """Representa un punto del poligono"""

    x: int = Field(ge=0)
    y: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


def _validate_polygon(points: list[Point]) -> list[Point]:
    """Valida la geometria de un poligono"""
    if len({(point.x, point.y) for point in points}) < 4:
        raise ValueError("El poligono debe contener al menos cuatro puntos distintos")
    area = abs(
        sum(
            point.x * points[(index + 1) % len(points)].y
            - points[(index + 1) % len(points)].x * point.y
            for index, point in enumerate(points)
        )
    )
    if area == 0:
        raise ValueError("Los puntos deben formar un poligono con area")
    return points


class ZoneCreate(BaseModel):
    """Valida la creacion de una zona"""

    name: str = Field(min_length=1, max_length=100)
    zone_type: ZoneType
    points: list[Point] = Field(min_length=4)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_polygon(self) -> "ZoneCreate":
        """Valida el poligono de la zona"""
        _validate_polygon(self.points)
        return self


class ZoneUpdate(BaseModel):
    """Valida la actualizacion de una zona"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    zone_type: ZoneType | None = None
    points: list[Point] | None = Field(default=None, min_length=4)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_update(self) -> "ZoneUpdate":
        """Valida los cambios de una zona"""
        if not self.model_fields_set:
            raise ValueError("Se debe proporcionar al menos un campo para actualizar")
        if self.points is not None:
            _validate_polygon(self.points)
        return self


class ZoneRead(BaseModel):
    """Representa la respuesta de una zona"""

    id: int
    camera_id: int
    name: str
    zone_type: ZoneType
    points: list[Point]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
