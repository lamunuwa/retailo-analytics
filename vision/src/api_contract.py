"""Define el contrato HTTP entre Vision y la API"""

from datetime import datetime
from typing import Literal, TypedDict

SessionTerminalStatus = Literal["completed", "failed"]


class PointContract(TypedDict):
    """Representa un punto de una zona"""

    x: int
    y: int


class ZoneContract(TypedDict):
    """Representa una zona recibida de la API"""

    id: int
    camera_id: int
    name: str
    zone_type: str
    points: list[PointContract]
    is_active: bool


class ZoneMetricContract(TypedDict):
    """Representa las metricas enviadas por zona"""

    zone_id: int
    visits: int
    dwell_seconds: float
    traffic_share: float


class VideoResultContract(TypedDict):
    """Representa el resultado enviado a la API"""

    processed_frames: int
    elapsed_seconds: float
    detected_people: int
    started_at: str
    finished_at: str
    zone_metrics: list[ZoneMetricContract]


def camera_zones_path(camera_id: int) -> str:
    """Construye la ruta de zonas de una camara"""
    return f"/cameras/{camera_id}/zones"


def camera_sessions_path(camera_id: int) -> str:
    """Construye la ruta de sesiones de una camara"""
    return f"/cameras/{camera_id}/sessions"


def session_path(session_id: int) -> str:
    """Construye la ruta de una sesion"""
    return f"/sessions/{session_id}"


def session_results_path(session_id: int) -> str:
    """Construye la ruta de resultados de una sesion"""
    return f"/sessions/{session_id}/video-results"


def session_create_payload(started_at: datetime) -> dict[str, str]:
    """Construye el cuerpo para crear una sesion"""
    return {"started_at": started_at.isoformat()}


def session_update_payload(
    status: SessionTerminalStatus,
    finished_at: datetime,
) -> dict[str, str]:
    """Construye el cuerpo para actualizar una sesion"""
    return {"status": status, "finished_at": finished_at.isoformat()}


def video_result_payload(
    *,
    processed_frames: int,
    elapsed_seconds: float,
    detected_people: int,
    started_at: datetime,
    finished_at: datetime,
    zone_metrics: list[ZoneMetricContract],
) -> VideoResultContract:
    """Construye el cuerpo de un resultado de video"""
    return {
        "processed_frames": processed_frames,
        "elapsed_seconds": elapsed_seconds,
        "detected_people": detected_people,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "zone_metrics": zone_metrics,
    }
