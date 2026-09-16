from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.cameras import CameraModel
from app.src.models.stores import StoreModel


class CameraRepositoryProtocol(Protocol):
    """Define las operaciones de camaras"""

    def create(
        self, store_id: int, name: str, source_type: str, description: str | None = None
    ) -> CameraModel | None:
        """Crea una camara para una tienda"""
        ...

    def get_all_by_store(self, store_id: int) -> list[CameraModel]:
        """Obtiene las camaras activas de una tienda"""
        ...

    def get_by_id(self, camera_id: int) -> CameraModel | None:
        """Obtiene una camara por identificador"""
        ...

    def update(
        self,
        camera_id: int,
        name: str | None = None,
        description: str | None = None,
        source_type: str | None = None,
        is_active: bool | None = None,
    ) -> CameraModel | None:
        """Actualiza una camara"""
        ...

    def delete(self, camera_id: int) -> CameraModel | None:
        """Desactiva una camara"""
        ...


class CameraRepository:
    """Gestiona la persistencia de camaras"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def create(
        self, store_id: int, name: str, source_type: str, description: str | None = None
    ) -> CameraModel | None:
        """Crea una camara para una tienda"""
        store = self.session.get(StoreModel, store_id)
        if store is None or not store.is_active:
            return None
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
        """Obtiene las camaras activas de una tienda"""
        stmt = select(CameraModel).where(
            CameraModel.store_id == store_id, CameraModel.is_active.is_(True)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, camera_id: int) -> CameraModel | None:
        """Obtiene una camara por identificador"""
        return self.session.get(CameraModel, camera_id)

    def update(
        self,
        camera_id: int,
        name: str | None = None,
        description: str | None = None,
        source_type: str | None = None,
        is_active: bool | None = None,
    ) -> CameraModel | None:
        """Actualiza una camara"""
        camera = self.session.get(CameraModel, camera_id)
        if camera is None:
            return None

        if name is not None:
            camera.name = name
        if description is not None:
            camera.description = description
        if source_type is not None:
            camera.source_type = source_type
        if is_active is not None:
            camera.is_active = is_active

        self.session.commit()
        self.session.refresh(camera)
        return camera

    def delete(self, camera_id: int) -> CameraModel | None:
        """Desactiva una camara"""
        camera = self.session.get(CameraModel, camera_id)
        if camera is None:
            return None
        camera.is_active = False
        self.session.commit()
        self.session.refresh(camera)
        return camera
