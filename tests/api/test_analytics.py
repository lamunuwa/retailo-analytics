from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.src.models.analytics import DetectionEvent
from app.src.repos.analytics import AnalyticsRepository
from app.src.routers.analytics import _to_response, get_detections
from app.src.schemas.analytics import DetectionEventCreate, DetectionFilters
from app.src.services.analytics import AnalyticsService


def make_event(camera_id: int = 1, zone_name: str = "Central") -> DetectionEvent:
    """Crea un evento de deteccion para pruebas"""
    return DetectionEvent(
        id=1,
        camera_id=camera_id,
        zone_name=zone_name,
        people_count=4,
        timestamp=datetime(2026, 9, 5, 12, tzinfo=UTC),
    )


def test_register_detection_service() -> None:
    """Valida el registro de una deteccion"""
    repo = MagicMock()
    service = AnalyticsService(repo)
    payload = DetectionEventCreate(
        camera_id=1,
        zone_name="Central",
        people_count=4,
        timestamp=datetime(2026, 9, 5, 12, tzinfo=UTC),
    )
    repo.create.return_value = make_event()

    result = service.register_detection(payload)

    assert result.id == 1
    repo.create.assert_called_once_with(payload)


def test_analytics_repository_applies_all_filters() -> None:
    """Valida los filtros del repositorio de analitica"""
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.order_by.return_value = query
    query.all.return_value = [make_event()]
    repository = AnalyticsRepository(db)
    filters = DetectionFilters(
        camera_id=1,
        zone_name="Central",
        start_date=datetime(2026, 9, 1, tzinfo=UTC),
        end_date=datetime(2026, 9, 5, tzinfo=UTC),
        limit=10,
        offset=5,
    )

    result = repository.get_all(filters)

    assert len(result) == 1
    assert query.filter.call_count == 4
    query.offset.assert_called_once_with(5)
    query.limit.assert_called_once_with(10)


def test_get_detections_router_passes_filters() -> None:
    """Valida los filtros del endpoint de detecciones"""
    service = MagicMock()
    service.get_detections.return_value = [make_event()]

    response = get_detections(
        service=service,
        camera_id=1,
        zone_name="Central",
        start_date=datetime(2026, 9, 1, tzinfo=UTC),
        end_date=datetime(2026, 9, 5, 23, 59, 59, tzinfo=UTC),
        limit=10,
        offset=5,
    )

    assert response[0].status == "received"
    service.get_detections.assert_called_once()
    filters = service.get_detections.call_args.args[0]
    assert filters == DetectionFilters(
        camera_id=1,
        zone_name="Central",
        start_date=datetime(2026, 9, 1, tzinfo=UTC),
        end_date=datetime(2026, 9, 5, 23, 59, 59, tzinfo=UTC),
        limit=10,
        offset=5,
    )


def test_get_detections_rejects_invalid_date_range() -> None:
    """Rechaza un rango de fechas invalido"""
    service = MagicMock()

    with pytest.raises(HTTPException) as exception:
        get_detections(
            service=service,
            start_date=datetime(2026, 9, 6, tzinfo=UTC),
            end_date=datetime(2026, 9, 5, tzinfo=UTC),
        )

    assert exception.value.status_code == 422
    service.get_detections.assert_not_called()


def test_legacy_naive_timestamp_is_returned_as_utc() -> None:
    """Normaliza una fecha sin zona horaria"""
    event = make_event()
    event.timestamp = datetime(2026, 9, 5, 12)

    assert _to_response(event).timestamp.tzinfo is UTC
