from app.src.models.stores import StoreModel


def test_store_model_defaults_is_active_to_true() -> None:
    store = StoreModel(name="Tienda demo")

    assert store.is_active is True
    