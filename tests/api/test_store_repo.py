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


def test_store_repository_lists_active_stores() -> None:
    mock_session = MagicMock()
    mock_session.scalars.return_value.all.return_value = [
        StoreModel(id=1, name="Tienda Activa", is_active=True)
    ]

    repo = StoreRepository(session=mock_session)

    stores = repo.get_all()

    assert len(stores) == 1
    assert stores[0].name == "Tienda Activa"


def test_store_repository_gets_store_by_id() -> None:
    mock_session = MagicMock()
    store = StoreModel(id=1, name="Tienda Centro", is_active=True)
    mock_session.get.return_value = store

    result = StoreRepository(session=mock_session).get_by_id(store_id=1)

    assert result is store
    mock_session.get.assert_called_once_with(StoreModel, 1)


def test_store_repository_soft_deletes_store() -> None:
    mock_session = MagicMock()
    tienda_mock = StoreModel(id=1, name="Tienda a borrar", is_active=True)
    mock_session.get.return_value = tienda_mock

    repo = StoreRepository(session=mock_session)

    repo.delete(store_id=1)

    assert tienda_mock.is_active is False
    mock_session.commit.assert_called_once()


def test_store_repository_updates_store() -> None:
    mock_session = MagicMock()
    tienda_mock = StoreModel(id=1, name="Nombre Viejo", is_active=True)
    mock_session.get.return_value = tienda_mock

    repo = StoreRepository(session=mock_session)

    updated_store = repo.update(store_id=1, name="Nombre Nuevo")

    assert tienda_mock.name == "Nombre Nuevo"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(tienda_mock)
    assert updated_store is tienda_mock
