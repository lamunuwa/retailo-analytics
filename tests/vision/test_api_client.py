from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from vision.src.api_client import APIClientError, RetailoAnalyticsClient
from vision.src.api_contract import (
    camera_sessions_path,
    camera_zones_path,
    session_path,
    session_results_path,
    video_result_payload,
)


def test_contract_builds_routes_and_result_payload() -> None:
    """Valida las rutas y el cuerpo de resultados"""
    now = datetime.now(UTC)
    payload = video_result_payload(
        processed_frames=10,
        elapsed_seconds=2.5,
        detected_people=3,
        started_at=now,
        finished_at=now,
        zone_metrics=[],
    )

    assert camera_zones_path(4) == "/cameras/4/zones"
    assert camera_sessions_path(4) == "/cameras/4/sessions"
    assert session_path(8) == "/sessions/8"
    assert session_results_path(8) == "/sessions/8/video-results"
    assert payload["processed_frames"] == 10
    assert payload["started_at"] == now.isoformat()


@patch("vision.src.api_client.requests.Session")
def test_client_uses_contract_for_complete_flow(session_class: MagicMock) -> None:
    """Valida el flujo HTTP completo de Vision"""
    http = session_class.return_value
    zones_response = MagicMock()
    zones_response.json.return_value = [
        {
            "id": 2,
            "camera_id": 4,
            "name": "Caja",
            "zone_type": "checkout",
            "points": [],
            "is_active": True,
        }
    ]
    create_response = MagicMock()
    create_response.json.return_value = {"id": 9}
    empty_response = MagicMock()
    empty_response.json.return_value = {}
    http.request.side_effect = [zones_response, create_response, empty_response, empty_response]
    client = RetailoAnalyticsClient("http://api:8000/", api_token="token", max_retries=0)
    now = datetime.now(UTC)

    assert client.get_zones(4)[0]["id"] == 2
    assert client.create_session(4, now) == 9
    payload = video_result_payload(
        processed_frames=1,
        elapsed_seconds=1,
        detected_people=1,
        started_at=now,
        finished_at=now,
        zone_metrics=[],
    )
    client.publish_video_result(9, payload)
    client.update_session(9, "failed", now)

    http.headers.__setitem__.assert_called_once_with("Authorization", "Bearer token")
    assert http.request.call_count == 4
    assert http.request.call_args_list[0].args == (
        "GET",
        "http://api:8000/cameras/4/zones",
    )


@patch("vision.src.api_client.requests.Session")
def test_client_wraps_network_and_contract_errors(session_class: MagicMock) -> None:
    """Valida los errores de red y contrato"""
    http = session_class.return_value
    response = MagicMock()
    response.raise_for_status.side_effect = requests.ConnectionError("offline")
    http.request.return_value = response
    client = RetailoAnalyticsClient("http://api:8000", max_retries=0)

    with pytest.raises(APIClientError, match="offline"):
        client.get_zones(1)

    response.raise_for_status.side_effect = None
    response.json.return_value = {"unexpected": True}
    with pytest.raises(APIClientError, match="zones"):
        client.get_zones(1)
    with pytest.raises(APIClientError, match="session id"):
        client.create_session(1, datetime.now(UTC))
