from typing import Protocol
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.src.models.cameras import CameraModel

class CameraRepositoryProtocol(Protocol):
    def create(
        self, 
        store_id: int, 
        name: str, 
        source_type: str, 
        description: str | None = None
    ) -> CameraModel:
        ...
    def get_all_by_store(self, store_id: int) -> list[CameraModel]:
        ...

class CameraRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self, 
        store_id: int, 
        name: str, 
        source_type: str, 
        description: str | None = None
    ) -> CameraModel:
        camera = CameraModel(
            store_id=store_id,
            name=name,
            source_type=source_type,
            description=description,
        )
        self.session.add(camera)
        self.session.commit()
        self.session.refresh(camera)
        return camera

    def get_all_by_store(self, store_id: int) -> list[CameraModel]:
        stmt = select(CameraModel).where(
            CameraModel.store_id == store_id,
            CameraModel.is_active.is_(True)
        )
        return list(self.session.scalars(stmt).all())