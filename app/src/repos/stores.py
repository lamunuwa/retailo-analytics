from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.stores import StoreModel


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
