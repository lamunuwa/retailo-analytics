from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.cameras import CameraModel
from app.src.models.zones import ZoneModel


class ZoneRepositoryProtocol(Protocol):
    """Define las operaciones de zonas"""

    def get_camera_by_id(self, camera_id: int) -> CameraModel | None:
        """Obtiene una camara por identificador"""
        ...

    def get_by_name(
        self, camera_id: int, name: str, exclude_id: int | None = None
    ) -> ZoneModel | None:
        """Obtiene una zona por nombre y camara"""
        ...

    def create(
        self,
        camera_id: int,
        name: str,
        zone_type: str,
        points: list[dict[str, int]],
    ) -> ZoneModel:
        """Crea una zona"""
        ...

    def get_all_by_camera(self, camera_id: int) -> list[ZoneModel]:
        """Obtiene las zonas activas de una camara"""
        ...

    def get_by_id(self, zone_id: int) -> ZoneModel | None:
        """Obtiene una zona por identificador"""
        ...

    def update(self, zone: ZoneModel, changes: dict[str, Any]) -> ZoneModel:
        """Actualiza una zona"""
        ...

    def delete(self, zone: ZoneModel) -> ZoneModel:
        """Desactiva una zona"""
        ...


class ZoneRepository:
    """Gestiona la persistencia de zonas"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def get_camera_by_id(self, camera_id: int) -> CameraModel | None:
        """Obtiene una camara por identificador"""
        return self.session.get(CameraModel, camera_id)

    def get_by_name(
        self, camera_id: int, name: str, exclude_id: int | None = None
    ) -> ZoneModel | None:
        """Obtiene una zona por nombre y camara"""
        stmt = select(ZoneModel).where(
            ZoneModel.camera_id == camera_id,
            ZoneModel.name == name,
        )
        if exclude_id is not None:
            stmt = stmt.where(ZoneModel.id != exclude_id)
        return self.session.scalar(stmt)

    def create(
        self,
        camera_id: int,
        name: str,
        zone_type: str,
        points: list[dict[str, int]],
    ) -> ZoneModel:
        """Crea una zona"""
        zone = ZoneModel(
            camera_id=camera_id,
            name=name,
            zone_type=zone_type,
            points=points,
        )
        self.session.add(zone)
        self.session.commit()
        self.session.refresh(zone)
        return zone

    def get_all_by_camera(self, camera_id: int) -> list[ZoneModel]:
        """Obtiene las zonas activas de una camara"""
        stmt = (
            select(ZoneModel)
            .where(ZoneModel.camera_id == camera_id, ZoneModel.is_active.is_(True))
            .order_by(ZoneModel.id)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, zone_id: int) -> ZoneModel | None:
        """Obtiene una zona por identificador"""
        return self.session.get(ZoneModel, zone_id)

    def update(self, zone: ZoneModel, changes: dict[str, Any]) -> ZoneModel:
        """Actualiza una zona"""
        for field, value in changes.items():
            setattr(zone, field, value)
        self.session.commit()
        self.session.refresh(zone)
        return zone

    def delete(self, zone: ZoneModel) -> ZoneModel:
        """Desactiva una zona"""
        zone.is_active = False
        self.session.commit()
        self.session.refresh(zone)
        return zone
