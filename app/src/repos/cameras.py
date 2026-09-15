from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.cameras import CameraModel


class CameraRepositoryProtocol(Protocol):
    """Define el contrato de operaciones de persistencia para la entidad Camera."""

    def create(
        self, store_id: int, name: str, source_type: str, description: str | None = None
    ) -> CameraModel:
        """Registra una nueva cámara asociada a una tienda."""
        ...

    def get_all_by_store(self, store_id: int) -> list[CameraModel]:
        """Obtiene todas las cámaras activas vinculadas a una tienda específica."""
        ...

    def get_by_id(self, camera_id: int) -> CameraModel | None:
        """Busca y retorna una cámara por su identificador único."""
        ...

    def update(
        self,
        camera_id: int,
        name: str | None = None,
        description: str | None = None,
        source_type: str | None = None,
        is_active: bool | None = None,
    ) -> CameraModel | None:
        """Actualiza de forma parcial los atributos de una cámara existente."""
        ...

    def soft_delete(self, camera_id: int) -> CameraModel | None: ...


class CameraRepository:
    """Implementación concreta del repositorio de cámaras utilizando SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con la sesión activa de base de datos."""
        self.session = session

    def create(
        self, store_id: int, name: str, source_type: str, description: str | None = None
    ) -> CameraModel:
        """Crea, persiste y retorna una nueva cámara en la base de datos."""
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
        """Consulta y retorna un listado de cámaras activas filtradas por su tienda."""
        stmt = select(CameraModel).where(
            CameraModel.store_id == store_id, CameraModel.is_active.is_(True)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, camera_id: int) -> CameraModel | None:
        """Busca y retorna un registro de cámara por su clave primaria, o None si no existe."""
        return self.session.get(CameraModel, camera_id)

    def update(
        self,
        camera_id: int,
        name: str | None = None,
        description: str | None = None,
        source_type: str | None = None,
        is_active: bool | None = None,
    ) -> CameraModel | None:
        """
        Modifica de manera selectiva los campos
        provistos de una cámara y persiste los cambios.
        """
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

    def soft_delete(self, camera_id: int) -> CameraModel | None:
        """Realiza un borrado lógico marcando is_active como False en la cámara."""
        camera = self.session.get(CameraModel, camera_id)
        if camera is None:
            return None
        camera.is_active = False
        self.session.commit()
        self.session.refresh(camera)
        return camera
