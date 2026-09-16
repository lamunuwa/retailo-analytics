from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.stores import StoreModel


class StoreRepositoryProtocol(Protocol):
    """Define las operaciones de tiendas"""

    def create(self, name: str) -> StoreModel:
        """Crea una tienda"""
        ...

    def get_all(self) -> list[StoreModel]:
        """Obtiene las tiendas activas"""
        ...

    def get_by_id(self, store_id: int) -> StoreModel | None:
        """Obtiene una tienda por identificador"""
        ...

    def delete(self, store_id: int) -> StoreModel | None:
        """Desactiva una tienda"""
        ...

    def update(
        self,
        store_id: int,
        name: str | None = None,
        is_active: bool | None = None,
    ) -> StoreModel | None:
        """Actualiza una tienda"""
        ...


class StoreRepository:
    """Gestiona la persistencia de tiendas"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def create(self, name: str) -> StoreModel:
        """Crea una tienda"""
        store = StoreModel(name=name)
        self.session.add(store)
        self.session.commit()
        self.session.refresh(store)
        return store

    def get_all(self) -> list[StoreModel]:
        """Obtiene las tiendas activas"""
        stmt = select(StoreModel).where(StoreModel.is_active.is_(True))
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, store_id: int) -> StoreModel | None:
        """Obtiene una tienda por identificador"""
        return self.session.get(StoreModel, store_id)

    def delete(self, store_id: int) -> StoreModel | None:
        """Desactiva una tienda"""
        store = self.session.get(StoreModel, store_id)
        if store is None:
            return None

        store.is_active = False
        self.session.commit()
        self.session.refresh(store)
        return store

    def update(
        self,
        store_id: int,
        name: str | None = None,
        is_active: bool | None = None,
    ) -> StoreModel | None:
        """Actualiza una tienda"""
        store = self.session.get(StoreModel, store_id)
        if store is None:
            return None

        if name is not None:
            store.name = name
        if is_active is not None:
            store.is_active = is_active
        self.session.commit()
        self.session.refresh(store)
        return store
