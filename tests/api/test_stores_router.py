from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.src.main import app
from app.src.models.stores import StoreModel

# Importamos la función de dependencia que usa el router
from app.src.routers.stores import get_store_repository


def test_create_store_endpoint() -> None:
    mock_repo = MagicMock()
    # Simulamos el retorno del método create
    mock_repo.create.return_value = StoreModel(id=1, name="Tienda Demo", is_active=True)

    # Inyectamos el mock sobrescribiendo la función exacta que FastAPI inyecta
    app.dependency_overrides[get_store_repository] = lambda: mock_repo

    client = TestClient(app)
    response = client.post("/stores", json={"name": "Tienda Demo"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Tienda Demo",
        "is_active": True,
    }

    app.dependency_overrides.clear()


def test_list_active_stores_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.get_all_active.return_value = [StoreModel(id=1, name="Tienda Activa", is_active=True)]

    app.dependency_overrides[get_store_repository] = lambda: mock_repo

    client = TestClient(app)
    response = client.get("/stores")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Tienda Activa"

    app.dependency_overrides.clear()


def test_soft_delete_store_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.soft_delete.return_value = StoreModel(id=1, name="Tienda a borrar", is_active=False)

    app.dependency_overrides[get_store_repository] = lambda: mock_repo

    client = TestClient(app)
    response = client.delete("/stores/1")

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    app.dependency_overrides.clear()


def test_create_store_without_name_returns_422() -> None:
    client = TestClient(app)

    response = client.post("/stores", json={})

    assert response.status_code == 422


def test_update_store_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.update.return_value = StoreModel(id=1, name="Nombre Nuevo", is_active=True)

    app.dependency_overrides[get_store_repository] = lambda: mock_repo

    client = TestClient(app)
    response = client.patch("/stores/1", json={"name": "Nombre Nuevo"})

    assert response.status_code == 200
    assert response.json()["name"] == "Nombre Nuevo"

    app.dependency_overrides.clear()
