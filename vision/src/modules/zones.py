from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import cv2
import numpy as np

Point = tuple[int, int]

# Configuracion temporal hasta recibir las zonas desde la API.
# Cada clave identifica una zona y cada tupla contiene puntos (x, y).
DEFAULT_ZONE_COORDINATES: dict[str, tuple[Point, ...]] = {
    "entrada": ((4, 6), (1909, 6), (1909, 1080), (6, 1080)),
}


@dataclass(frozen=True)
class RoiZone:
    """Representa una zona definida mediante puntos"""

    name: str
    points: tuple[Point, ...]

    @property
    def contour(self) -> np.ndarray:
        """Convierte los puntos al formato requerido por OpenCV"""

        contour = np.array(self.points, dtype=np.int32)
        return contour

    def contains(self, point: tuple[float, float]) -> bool:
        """Indica si un punto pertenece a la zona, incluidos sus bordes"""

        is_inside = cv2.pointPolygonTest(self.contour, point, False) >= 0
        return is_inside


# Funciones de apoyo ---------------------------------------


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

    zones = build_zones(DEFAULT_ZONE_COORDINATES)
    return zones


# ----------------------------------------------------------
