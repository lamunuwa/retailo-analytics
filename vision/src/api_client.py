"""Comunica Vision con la API de RetaiLO Analytics"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from vision.src.api_contract import (
    SessionTerminalStatus,
    VideoResultContract,
    ZoneContract,
    camera_sessions_path,
    camera_zones_path,
    session_create_payload,
    session_path,
    session_results_path,
    session_update_payload,
)

@dataclass(frozen=True)
class CameraZone:
    """Representa una zona obtenida desde la API."""

    id: int
    name: str
    points: tuple[tuple[int, int], ...]


class APIClientError(Exception):
    """Excepción lanzada cuando falla la comunicación con la API."""

class APIClientError(Exception):
    """Representa un error de comunicacion con la API"""


class RetailoAnalyticsClient:
    """Gestiona las solicitudes HTTP hacia la API"""

    def __init__(
        self,
        api_url: str,
        api_token: str = "",
        timeout_seconds: float = 10,
        max_retries: int = 3,
    ) -> None:
        """Inicializa el cliente HTTP"""
        self.api_url = api_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        if api_token:
            self.session.headers["Authorization"] = f"Bearer {api_token}"
        retry = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 502, 503, 504),
            # Evita reintentar POST para no duplicar datos sin idempotencia
            allowed_methods=frozenset({"GET"}),
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Ejecuta una solicitud y valida su respuesta"""
        url = f"{self.api_url}{path}"
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout_seconds,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            raise APIClientError(f"Fallo en API {method} {url}: {error}") from error

    def get_zones(self, camera_id: int) -> list[ZoneContract]:
        """Obtiene las zonas de una camara"""
        data = self._request("GET", camera_zones_path(camera_id))
        if not isinstance(data, list):
            raise APIClientError("La API devolvio un contrato invalido para zones")
        return cast(list[ZoneContract], data)

    def create_session(self, camera_id: int, started_at: datetime) -> int:
        """Crea una sesion y obtiene su identificador"""
        data = self._request(
            "POST",
            camera_sessions_path(camera_id),
            json=session_create_payload(started_at),
        )
        try:
            return int(data["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise APIClientError("La API no devolvio un session id valido") from error

    def publish_video_result(
        self,
        session_id: int,
        payload: VideoResultContract,
    ) -> None:
        """Publica el resultado de una sesion"""
        self._request("POST", session_results_path(session_id), json=payload)

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
        status: SessionTerminalStatus,
        finished_at: datetime,
    ) -> None:
        """Actualiza el estado de una sesion"""
        self._request(
            "PATCH",
            session_path(session_id),
            json=session_update_payload(status, finished_at),
        )
