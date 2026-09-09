from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.src.main import app
from app.src.models.analytics import DetectionEvent
from app.src.routers.analytics import get_analytics_service
from app.src.schemas.analytics import DetectionEventCreate
from app.src.services.analytics import AnalyticsService

client = TestClient(app)


def test_register_detection_service() -> None:
    """Prueba unitaria para el servicio de analítica utilizando mocks."""
    mock_repo = MagicMock()
    service = AnalyticsService(mock_repo)

    payload = DetectionEventCreate(
        camera_id=1,
        zone_name="Pasillo Central",
        people_count=4,
        timestamp="2026-09-05T12:00:00Z",  # type: ignore[arg-type]
    )

    mock_repo.create.return_value = DetectionEvent(
        id=1,
        camera_id=1,
        zone_name="Pasillo Central",
        people_count=4,
        timestamp="2026-09-05T12:00:00Z",
    )

    result = service.register_detection(payload)

    assert result.id == 1
    assert result.people_count == 4
    mock_repo.create.assert_called_once_with(payload)


def test_ingest_detection_router() -> None:
    """Prueba de integración del endpoint POST /analytics/detections usando dependency overrides."""
    mock_service = MagicMock()
    mock_service.register_detection.return_value = DetectionEvent(
        id=1,
        camera_id=1,
        zone_name="Pasillo Central",
        people_count=4,
        timestamp="2026-09-05T12:00:00Z",
    )

    app.dependency_overrides[get_analytics_service] = lambda: mock_service

    payload = {
        "camera_id": 1,
        "zone_name": "Pasillo Central",
        "people_count": 4,
        "timestamp": "2026-09-05T12:00:00Z",
    }
    response = client.post("/analytics/detections", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["camera_id"] == 1
    assert data["status"] == "received"

    app.dependency_overrides.clear()


def test_get_detections_router() -> None:
    """Prueba de integración del endpoint GET /analytics/detections usando dependency overrides."""
    mock_service = MagicMock()
    mock_service.get_detections.return_value = [
        DetectionEvent(
            id=1,
            camera_id=1,
            zone_name="Pasillo Central",
            people_count=4,
            timestamp="2026-09-05T12:00:00Z",
        )
    ]

    app.dependency_overrides[get_analytics_service] = lambda: mock_service

    response = client.get("/analytics/detections")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["camera_id"] == 1
    assert data[0]["zone_name"] == "Pasillo Central"

    app.dependency_overrides.clear()