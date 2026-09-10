"""Cliente HTTP para comunicarse con la API de RetaiLO Analytics."""

from datetime import datetime
from typing import Literal

import requests


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
