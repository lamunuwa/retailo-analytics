from datetime import UTC, datetime
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.src.main import app
from app.src.models.cameras import CameraModel
from app.src.routers.cameras import get_camera_repository

def test_create_camera_endpoint() -> None:
    # 1. Configurar el Mock con una fecha válida para created_at
    mock_repo = MagicMock()
    mock_repo.create.return_value = CameraModel(
        id=1, 
        store_id=5, 
        name="Cámara Pasillo", 
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    
    # Reemplazar la dependencia real por el mock
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)
    
    # 2. Ejecutar la petición
    response = client.post(
        "/stores/5/cameras", 
        json={"name": "Cámara Pasillo", "source_type": "demo_video"}
    )
    
    # 3. Validaciones
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["store_id"] == 5
    assert data["name"] == "Cámara Pasillo"
    assert data["is_active"] is True
    
    # Limpiar overrides
    app.dependency_overrides.clear()

def test_list_cameras_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.get_all_by_store.return_value = [
        CameraModel(
            id=1, 
            store_id=5, 
            name="Cámara Pasillo", 
            source_type="demo_video",
            is_active=True,
            created_at=datetime.now(UTC)
        )
    ]
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)
    
    response = client.get("/stores/5/cameras")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Cámara Pasillo"
    
    app.dependency_overrides.clear()

def test_get_camera_by_id_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = CameraModel(
        id=1, 
        store_id=5, 
        name="Cámara Principal", 
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)
    
    response = client.get("/cameras/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Cámara Principal"
    
    app.dependency_overrides.clear()

def test_get_camera_not_found_returns_404() -> None:
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)
    
    response = client.get("/cameras/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Camera not found"
    
    app.dependency_overrides.clear()

def test_update_camera_endpoint() -> None:
    #agrega la prueba para el endpoint de actualización
    mock_repo = MagicMock()
    mock_repo.update.return_value = CameraModel(
        id=1, 
        store_id=5, 
        name="Cámara Actualizada", 
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    app.dependency_overrides[get_camera_repository] = lambda: mock_repo
    client = TestClient(app)
    
    response = client.patch("/cameras/1", json={"name": "Cámara Actualizada"})
    assert response.status_code == 200
    assert response.json()["name"] == "Cámara Actualizada"
    
    app.dependency_overrides.clear()