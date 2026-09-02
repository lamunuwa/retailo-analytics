from unittest.mock import MagicMock

from app.src.models.stores import StoreModel
from app.src.repos.stores import StoreRepository


def test_store_model_defaults_is_active_to_true() -> None:
    store = StoreModel(name="Tienda demo")

    assert store.is_active is True


def test_store_repository_creates_store() -> None:
    mock_session = MagicMock()
    repo = StoreRepository(session=mock_session)

    store = repo.create(name="Sucursal Centro")

    assert isinstance(store, StoreModel)
    assert store.name == "Sucursal Centro"
    assert store.is_active is True
    mock_session.add.assert_called_once_with(store)
    mock_session.commit.assert_called_once()
