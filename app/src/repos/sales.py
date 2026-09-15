from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.cameras import CameraModel
from app.src.models.sales import SalesRecordModel
from app.src.models.stores import StoreModel
from app.src.models.zones import ZoneModel
from app.src.schemas.sales import SalesRecordCreate


class SalesRepositoryProtocol(Protocol):
    """Define las operaciones de ventas"""

    def get_store_by_id(self, store_id: int) -> StoreModel | None:
        """Obtiene una tienda por identificador"""
        ...

    def get_zone_by_store(self, store_id: int, zone_id: int) -> ZoneModel | None:
        """Obtiene una zona de una tienda"""
        ...

    def create(self, store_id: int, payload: SalesRecordCreate) -> SalesRecordModel:
        """Crea un registro de venta"""
        ...

    def get_all_by_store(
        self,
        store_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[SalesRecordModel]:
        """Obtiene las ventas de una tienda"""
        ...


class SalesRepository:
    """Gestiona la persistencia de ventas"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def get_store_by_id(self, store_id: int) -> StoreModel | None:
        """Obtiene una tienda por identificador"""
        return self.session.get(StoreModel, store_id)

    def get_zone_by_store(self, store_id: int, zone_id: int) -> ZoneModel | None:
        """Obtiene una zona de una tienda"""
        stmt = (
            select(ZoneModel)
            .join(CameraModel, CameraModel.id == ZoneModel.camera_id)
            .where(ZoneModel.id == zone_id, CameraModel.store_id == store_id)
        )
        return self.session.scalar(stmt)

    def create(self, store_id: int, payload: SalesRecordCreate) -> SalesRecordModel:
        """Crea un registro de venta"""
        record = SalesRecordModel(store_id=store_id, **payload.model_dump())
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_all_by_store(
        self,
        store_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[SalesRecordModel]:
        """Obtiene las ventas de una tienda"""
        stmt = select(SalesRecordModel).where(SalesRecordModel.store_id == store_id)
        if start_date is not None:
            stmt = stmt.where(SalesRecordModel.recorded_at >= start_date)
        if end_date is not None:
            stmt = stmt.where(SalesRecordModel.recorded_at <= end_date)
        stmt = stmt.order_by(SalesRecordModel.recorded_at.desc(), SalesRecordModel.id.desc())
        return list(self.session.scalars(stmt).all())
