"""Cliente HTTP para comunicarse con la API de RetaiLO Analytics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, cast

import requests


@dataclass(frozen=True)
class CameraZone:
    """Representa una zona obtenida desde la API."""

    id: int
    name: str
    points: tuple[tuple[int, int], ...]


class APIClientError(Exception):
    """Excepción lanzada cuando falla la comunicación con la API."""

    pass


class RetailoAnalyticsClient:
    """Cliente HTTP para comunicarse con la API de RetaiLO Analytics."""

    def __init__(self, api_url: str) -> None:
        """Inicializa el cliente con la URL base de la API."""

        self.api_url = api_url.rstrip("/")

    def create_session(
        self,
        camera_id: int,
        started_at: datetime,
    ) -> int:
        """Crea una sesión en la API y retorna el session_id."""

        url = f"{self.api_url}/cameras/{camera_id}/sessions"
        payload = {
            "started_at": started_at.isoformat(),
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            session_id: int = data["id"]
            return session_id
        except requests.exceptions.RequestException as e:
            raise APIClientError(
                f"Fallo al crear sesión en API ({url}): {str(e)}"
            ) from e

    def get_zones(self, camera_id: int) -> tuple[CameraZone, ...]:
        """Obtiene las zonas activas de una camara."""
        url = f"{self.api_url}/cameras/{camera_id}/zones"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return tuple(
                CameraZone(
                    id=int(item["id"]),
                    name=str(item["name"]),
                    points=tuple((int(point["x"]), int(point["y"])) for point in item["points"]),
                )
                for item in response.json()
                if item.get("is_active", True)
            )
        except (KeyError, TypeError, ValueError, requests.exceptions.RequestException) as error:
            raise APIClientError(
                f"Fallo al consultar zonas en API ({url}): {str(error)}"
            ) from error

    def create_video_result(
        self,
        session_id: int,
        processed_frames: int,
        elapsed_seconds: float,
        detected_people: int,
        started_at: datetime,
        finished_at: datetime,
        zone_metrics: list[dict[str, int | float]],
    ) -> None:
        """Publica el resultado agregado de una sesion."""
        url = f"{self.api_url}/sessions/{session_id}/video-results"
        payload = {
            "processed_frames": processed_frames,
            "elapsed_seconds": elapsed_seconds,
            "detected_people": detected_people,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "zone_metrics": zone_metrics,
        }
        try:
            response = requests.post(url, json=cast(Any, payload), timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise APIClientError(
                f"Fallo al publicar resultados en API ({url}): {str(error)}"
            ) from error

    def update_session(
        self,
        session_id: int,
        status: Literal["completed", "failed"],
        finished_at: datetime,
    ) -> None:
        """Actualiza el estado de una sesión en la API."""

        url = f"{self.api_url}/sessions/{session_id}"
        payload = {
            "status": status,
            "finished_at": finished_at.isoformat(),
        }

        try:
            response = requests.patch(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIClientError(
                f"Fallo al actualizar sesión en API ({url}): {str(e)}"
            ) from e
