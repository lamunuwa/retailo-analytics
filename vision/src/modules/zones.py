from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import cv2
import numpy as np

from vision.src.api_contract import ZoneContract

Point = tuple[int, int]

DEFAULT_ZONE_COORDINATES: dict[str, tuple[Point, ...]] = {
    "entrada": ((4, 6), (1909, 6), (1909, 1080), (6, 1080)),
}


@dataclass(frozen=True)
class RoiZone:
    """Representa una zona definida mediante puntos"""

    name: str
    points: tuple[Point, ...]
    zone_id: int | None = None

    @property
    def contour(self) -> np.ndarray:
        """Convierte los puntos al formato requerido por OpenCV"""
        return np.array(self.points, dtype=np.int32)

    def contains(self, point: tuple[float, float]) -> bool:
        """Indica si un punto pertenece a la zona, incluidos sus bordes"""

        return cv2.pointPolygonTest(self.contour, point, False) >= 0


def validate_zone_points(
    zone_name: str,
    zone_points: Sequence[Point],
) -> None:
    """Valida que una zona tenga puntos suficientes para formar un poligono"""

    if len(zone_points) < 3:
        raise ValueError(f"La zona '{zone_name}' debe tener al menos 3 puntos")


def build_zones(
    zone_coordinates: Mapping[str, Sequence[Point]],
) -> tuple[RoiZone, ...]:
    """Convierte las coordenadas configuradas en zonas ROI"""

    if not zone_coordinates:
        raise ValueError("Se requiere al menos una zona ROI")

    configured_zones: list[RoiZone] = []

    for zone_name, zone_points in zone_coordinates.items():
        validate_zone_points(zone_name, zone_points)

        zone = RoiZone(
            name=zone_name,
            points=tuple(zone_points),
        )
        configured_zones.append(zone)

    return tuple(configured_zones)


def get_configured_zones() -> tuple[RoiZone, ...]:
    """Obtiene las zonas configuradas para la deteccion"""
    return build_zones(DEFAULT_ZONE_COORDINATES)


def build_zones_from_api(zones: Sequence[ZoneContract]) -> tuple[RoiZone, ...]:
    """Convierte zonas de la API al formato de OpenCV"""

    if not zones:
        raise ValueError("La camara no tiene zonas activas configuradas en la API")
    output: list[RoiZone] = []
    for zone in zones:
        points = tuple((point["x"], point["y"]) for point in zone["points"])
        validate_zone_points(zone["name"], points)
        output.append(RoiZone(name=zone["name"], points=points, zone_id=zone["id"]))
    return tuple(output)
