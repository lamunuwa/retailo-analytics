import json
from unittest.mock import MagicMock

from app.src.main import app, root
from app.src.routers.health import health_check


def test_root_redirects_to_docs() -> None:
    response = root()

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_health_check_reports_database_status() -> None:
    db = MagicMock()
    response = health_check(db=db)
    body = json.loads(bytes(response.body))

    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["checks"]["database"]["status"] == "healthy"


def test_health_check_reports_degraded_when_database_is_unavailable() -> None:
    db = MagicMock()
    db.execute.side_effect = RuntimeError("database unavailable")
    response = health_check(db=db)
    body = json.loads(bytes(response.body))

    assert response.status_code == 503
    assert body["status"] == "degraded"
    assert body["checks"]["database"]["status"] == "unhealthy"


def test_openapi_lists_store_operations_in_requested_order() -> None:
    schema = app.openapi()

    assert list(schema["paths"]["/stores/"].keys()) == ["post", "get"]
    assert list(schema["paths"]["/stores/{store_id}"].keys()) == ["get", "patch", "delete"]
