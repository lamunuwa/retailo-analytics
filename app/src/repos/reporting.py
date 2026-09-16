from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.src.models.cameras import CameraModel
from app.src.models.results import VideoResultModel
from app.src.models.sales import SalesRecordModel
from app.src.models.sessions import SessionModel
from app.src.models.stores import StoreModel
from app.src.models.zones import ZoneModel


class ReportingRepositoryProtocol(Protocol):
    """Define las consultas para generar reportes"""

    def get_store_by_id(self, store_id: int) -> StoreModel | None:
        """Obtiene una tienda por identificador"""
        ...

    def get_all_zones_by_store(self, store_id: int) -> list[ZoneModel]:
        """Obtiene las zonas de una tienda"""
        ...

    def get_all_results_by_store(
        self,
        store_id: int,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[VideoResultModel]:
        """Obtiene los resultados de una tienda"""
        ...

    def get_all_sales_by_store(
        self,
        store_id: int,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[SalesRecordModel]:
        """Obtiene las ventas de una tienda"""
        ...


class ReportingRepository:
    """Consulta los datos necesarios para reportes"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def get_store_by_id(self, store_id: int) -> StoreModel | None:
        """Obtiene una tienda por identificador"""
        return self.session.get(StoreModel, store_id)

    def get_all_zones_by_store(self, store_id: int) -> list[ZoneModel]:
        """Obtiene las zonas de una tienda"""
        stmt = (
            select(ZoneModel)
            .join(CameraModel, CameraModel.id == ZoneModel.camera_id)
            .where(CameraModel.store_id == store_id)
            .order_by(ZoneModel.id)
        )
        return list(self.session.scalars(stmt).all())

    def get_all_results_by_store(
        self,
        store_id: int,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[VideoResultModel]:
        """Obtiene los resultados de una tienda"""
        stmt = (
            select(VideoResultModel)
            .options(selectinload(VideoResultModel.zone_metrics))
            .join(SessionModel, SessionModel.id == VideoResultModel.session_id)
            .join(CameraModel, CameraModel.id == SessionModel.camera_id)
            .where(CameraModel.store_id == store_id)
        )
        if start_date is not None:
            stmt = stmt.where(VideoResultModel.started_at >= start_date)
        if end_date is not None:
            stmt = stmt.where(VideoResultModel.finished_at <= end_date)
        return list(self.session.scalars(stmt).unique().all())

    def get_all_sales_by_store(
        self,
        store_id: int,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[SalesRecordModel]:
        """Obtiene las ventas de una tienda"""
        stmt = select(SalesRecordModel).where(SalesRecordModel.store_id == store_id)
        if start_date is not None:
            stmt = stmt.where(SalesRecordModel.recorded_at >= start_date)
        if end_date is not None:
            stmt = stmt.where(SalesRecordModel.recorded_at <= end_date)
        return list(self.session.scalars(stmt).all())
