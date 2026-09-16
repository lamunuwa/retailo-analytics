from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from vision.src.api_client import APIClientError, CameraZone, RetailoAnalyticsClient


def test_create_session_returns_api_identifier() -> None:
    response = MagicMock()
    response.json.return_value = {"id": 17}

    with patch("vision.src.api_client.requests.post", return_value=response) as post:
        client = RetailoAnalyticsClient("http://api:8000/")
        started_at = datetime(2026, 9, 15, 12, 30, tzinfo=UTC)

        session_id = client.create_session(camera_id=4, started_at=started_at)

    assert session_id == 17
    assert client.api_url == "http://api:8000"
    post.assert_called_once_with(
        "http://api:8000/cameras/4/sessions",
        json={"started_at": "2026-09-15T12:30:00+00:00"},
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()


def test_get_zones_returns_only_active_zones() -> None:
    response = MagicMock()
    response.json.return_value = [
        {
            "id": "7",
            "name": "entrada",
            "points": [{"x": "1", "y": "2"}, {"x": 3, "y": 4}, {"x": 5, "y": 6}],
        },
        {
            "id": 8,
            "name": "inactiva",
            "points": [{"x": 10, "y": 20}],
            "is_active": False,
        },
    ]

    with patch("vision.src.api_client.requests.get", return_value=response) as get:
        zones = RetailoAnalyticsClient("http://api:8000").get_zones(camera_id=4)

    assert zones == (
        CameraZone(id=7, name="entrada", points=((1, 2), (3, 4), (5, 6))),
    )
    get.assert_called_once_with("http://api:8000/cameras/4/zones", timeout=10)
    response.raise_for_status.assert_called_once_with()


def test_create_video_result_posts_aggregated_metrics() -> None:
    response = MagicMock()
    started_at = datetime(2026, 9, 15, 12, 30, tzinfo=UTC)
    finished_at = datetime(2026, 9, 15, 12, 31, tzinfo=UTC)
    zone_metrics: list[dict[str, int | float]] = [
        {"zone_id": 7, "visits": 3, "dwell_seconds": 0.0, "traffic_share": 100.0}
    ]

    with patch("vision.src.api_client.requests.post", return_value=response) as post:
        RetailoAnalyticsClient("http://api:8000").create_video_result(
            session_id=17,
            processed_frames=30,
            elapsed_seconds=60.0,
            detected_people=3,
            started_at=started_at,
            finished_at=finished_at,
            zone_metrics=zone_metrics,
        )

    post.assert_called_once_with(
        "http://api:8000/sessions/17/video-results",
        json={
            "processed_frames": 30,
            "elapsed_seconds": 60.0,
            "detected_people": 3,
            "started_at": "2026-09-15T12:30:00+00:00",
            "finished_at": "2026-09-15T12:31:00+00:00",
            "zone_metrics": zone_metrics,
        },
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()


def test_update_session_patches_status() -> None:
    response = MagicMock()
    finished_at = datetime(2026, 9, 15, 12, 31, tzinfo=UTC)

    with patch("vision.src.api_client.requests.patch", return_value=response) as patch_request:
        RetailoAnalyticsClient("http://api:8000").update_session(
            session_id=17,
            status="completed",
            finished_at=finished_at,
        )

    patch_request.assert_called_once_with(
        "http://api:8000/sessions/17",
        json={"status": "completed", "finished_at": "2026-09-15T12:31:00+00:00"},
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize(
    ("request_name", "operation", "expected_url"),
    [
        (
            "post",
            "create_session",
            "http://api:8000/cameras/4/sessions",
        ),
        (
            "get",
            "get_zones",
            "http://api:8000/cameras/4/zones",
        ),
        (
            "post",
            "create_video_result",
            "http://api:8000/sessions/17/video-results",
        ),
        (
            "patch",
            "update_session",
            "http://api:8000/sessions/17",
        ),
    ],
)
def test_request_errors_are_exposed_as_api_client_errors(
    request_name: str,
    operation: str,
    expected_url: str,
) -> None:
    client = RetailoAnalyticsClient("http://api:8000")
    timestamp = datetime(2026, 9, 15, tzinfo=UTC)

    with (
        patch(
            f"vision.src.api_client.requests.{request_name}",
            side_effect=requests.exceptions.ConnectionError("sin conexion"),
        ),
        pytest.raises(APIClientError, match=expected_url),
    ):
        if operation == "create_session":
            client.create_session(camera_id=4, started_at=timestamp)
        elif operation == "get_zones":
            client.get_zones(camera_id=4)
        elif operation == "create_video_result":
            client.create_video_result(
                session_id=17,
                processed_frames=0,
                elapsed_seconds=0.0,
                detected_people=0,
                started_at=timestamp,
                finished_at=timestamp,
                zone_metrics=[],
            )
        else:
            client.update_session(session_id=17, status="failed", finished_at=timestamp)


def test_get_zones_wraps_invalid_api_data() -> None:
    response = MagicMock()
    response.json.return_value = [{"id": 7}]

    with (
        patch("vision.src.api_client.requests.get", return_value=response),
        pytest.raises(APIClientError, match="Fallo al consultar zonas"),
    ):
        RetailoAnalyticsClient("http://api:8000").get_zones(camera_id=4)
