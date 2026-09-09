from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.src.main import app
from app.src.models.cameras import CameraModel
from app.src.routers.cameras import get_camera_repository


def test_create_camera_endpoint() -> None:
    """Verifica que el endpoint POST registre una cámara correctamente."""
    mock_repo = MagicMock()
    mock_repo.create.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara Pasillo",
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    # Configura la inyección de dependencias con el repositorio simulado
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)

    # Ejecuta la petición POST al endpoint de creación
    response = client.post(
        "/stores/5/cameras", json={"name": "Cámara Pasillo", "source_type": "demo_video"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Cámara Pasillo"
    assert data["source_type"] == "demo_video"

    # Valida que el repositorio haya recibido los datos exactos
    mock_repo.create.assert_called_once_with(
        store_id=5,
        name="Cámara Pasillo",
        source_type="demo_video",
        description=None,
    )

    app.dependency_overrides.clear()


def test_list_cameras_endpoint() -> None:
    """Verifica que el endpoint GET liste las cámaras activas de una tienda."""
    mock_repo = MagicMock()
    mock_repo.get_all_by_store.return_value = [
        CameraModel(
            id=1,
            store_id=5,
            name="Cámara Pasillo",
            source_type="demo_video",
            is_active=True,
            created_at=datetime.now(UTC),
        )
    ]
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)

    # Consulta el listado de cámaras por tienda
    response = client.get("/stores/5/cameras")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Cámara Pasillo"

    mock_repo.get_all_by_store.assert_called_once_with(store_id=5)

    app.dependency_overrides.clear()


def test_get_camera_by_id_endpoint() -> None:
    """Verifica que el endpoint GET obtenga una cámara específica por su ID."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara Principal",
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)

    # Solicita el detalle de una cámara por ID
    response = client.get("/cameras/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cámara Principal"

    mock_repo.get_by_id.assert_called_once_with(camera_id=1)

    app.dependency_overrides.clear()


def test_get_camera_not_found_returns_404() -> None:
    """Verifica que se devuelva un error 404 si la cámara consultada no existe."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)

    response = client.get("/cameras/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Camera not found"

    app.dependency_overrides.clear()


def test_update_camera_endpoint() -> None:
    """Verifica la actualización parcial (PATCH) de una cámara existente."""
    mock_repo = MagicMock()
    mock_repo.update.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara Actualizada",
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)

    # Envía los campos a modificar mediante PATCH
    response = client.patch("/cameras/1", json={"name": "Cámara Actualizada"})
    assert response.status_code == 200
    assert response.json()["name"] == "Cámara Actualizada"

    # Confirma que el repositorio procesó los valores esperados
    mock_repo.update.assert_called_once_with(
        camera_id=1,
        name="Cámara Actualizada",
        description=None,
        source_type=None,
        is_active=None,
    )

    app.dependency_overrides.clear()


def test_soft_delete_camera_endpoint() -> None:
    """Verifica el borrado lógico (DELETE) cambiando el estado is_active a False."""
    mock_repo = MagicMock()
    mock_repo.soft_delete.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara a borrar",
        source_type="demo_video",
        is_active=False,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)

    # Ejecuta la petición DELETE para desactivar lógicamente el recurso
    response = client.delete("/cameras/1")
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    mock_repo.soft_delete.assert_called_once_with(camera_id=1)

    app.dependency_overrides.clear()