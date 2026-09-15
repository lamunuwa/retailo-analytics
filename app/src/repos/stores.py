from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.stores import StoreModel


class StoreRepositoryProtocol(Protocol):
    def create(self, name: str) -> StoreModel: ...

    def get_all_active(self) -> list[StoreModel]: ...

    def get_by_id(self, store_id: int) -> StoreModel | None: ...

    def soft_delete(self, store_id: int) -> StoreModel | None: ...

    def update(self, store_id: int, name: str | None = None) -> StoreModel | None: ...


class StoreRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str) -> StoreModel:
        store = StoreModel(name=name)
        self.session.add(store)
        self.session.commit()
        self.session.refresh(store)
        return store

    def get_all_active(self) -> list[StoreModel]:
        stmt = select(StoreModel).where(StoreModel.is_active.is_(True))
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, store_id: int) -> StoreModel | None:
        return self.session.get(StoreModel, store_id)

    def soft_delete(self, store_id: int) -> StoreModel | None:
        store = self.session.get(StoreModel, store_id)
        if store is None:
            return None

        store.is_active = False
        self.session.commit()
        self.session.refresh(store)
        return store

    def update(self, store_id: int, name: str | None = None) -> StoreModel | None:
        store = self.session.get(StoreModel, store_id)
        if store is None:
            return None

        if name is not None:
            store.name = name
        self.session.commit()
        self.session.refresh(store)
        return store
