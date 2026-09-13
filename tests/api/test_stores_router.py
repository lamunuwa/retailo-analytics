from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.src.models.stores import StoreModel
from app.src.routers.stores import (
    create_store,
    get_store,
    list_stores,
    soft_delete_store,
    update_store,
)
from app.src.schemas.stores import StoreCreate, StoreUpdate


def test_create_store_endpoint() -> None:
    mock_repo = MagicMock()
    # Simulamos el retorno del método create
    mock_repo.create.return_value = StoreModel(id=1, name="Tienda Demo", is_active=True)

    response = create_store(payload=StoreCreate(name="Tienda Demo"), repo=mock_repo)

    assert response.name == "Tienda Demo"
    mock_repo.create.assert_called_once_with(name="Tienda Demo")


def test_list_active_stores_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.get_all_active.return_value = [StoreModel(id=1, name="Tienda Activa", is_active=True)]

    response = list_stores(repo=mock_repo)

    assert len(response) == 1
    assert response[0].name == "Tienda Activa"


def test_get_store_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = StoreModel(id=1, name="Tienda Centro", is_active=True)
    response = get_store(store_id=1, repo=mock_repo)

    assert response.name == "Tienda Centro"
    mock_repo.get_by_id.assert_called_once_with(1)


def test_soft_delete_store_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.soft_delete.return_value = StoreModel(id=1, name="Tienda a borrar", is_active=False)

    response = soft_delete_store(store_id=1, repo=mock_repo)

    assert response.is_active is False


def test_create_store_without_name_returns_422() -> None:
    with pytest.raises(ValidationError):
        StoreCreate.model_validate({})


def test_update_store_endpoint() -> None:
    mock_repo = MagicMock()
    mock_repo.update.return_value = StoreModel(id=1, name="Nombre Nuevo", is_active=True)

    response = update_store(
        store_id=1,
        payload=StoreUpdate(name="Nombre Nuevo"),
        repo=mock_repo,
    )

    assert response.name == "Nombre Nuevo"
    mock_repo.update.assert_called_once_with(store_id=1, name="Nombre Nuevo")


def test_update_store_without_fields_returns_422() -> None:
    with pytest.raises(ValidationError):
        StoreUpdate()


def test_get_missing_store_raises_404() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exception:
        get_store(store_id=999, repo=repo)

    assert exception.value.status_code == 404
