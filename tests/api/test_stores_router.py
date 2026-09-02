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