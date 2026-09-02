from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.src.main import app
from app.src.models.stores import StoreModel
from app.src.repos.stores import StoreRepository


def test_create_store_endpoint() -> None:
    mock_repo = MagicMock()
    # Simulamos el retorno del método create
    mock_repo.create.return_value = StoreModel(id=1, name="Tienda Demo", is_active=True)

    # Inyectamos el mock en la aplicación
    app.dependency_overrides[StoreRepository] = lambda: mock_repo

    client = TestClient(app)
    response = client.post("/stores", json={"name": "Tienda Demo"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Tienda Demo",
        "is_active": True,
    }

    app.dependency_overrides.clear()