from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.cameras import CameraModel
from app.src.models.sessions import SessionModel


class SessionRepositoryProtocol(Protocol):
    """Define el contrato de operaciones de persistencia para la entidad Session."""

    def create(
        self,
        camera_id: int,
        started_at: datetime,
    ) -> SessionModel | None:
        """Registra una nueva sesión de video asociada a una cámara."""
        ...

    def get_by_id(self, session_id: int) -> SessionModel | None:
        """Busca y retorna una sesión por su identificador único."""
        ...

    def update(
        self,
        session_id: int,
        status: str,
        finished_at: datetime,
    ) -> SessionModel | None:
        """Actualiza de forma parcial los atributos de una sesión existente."""
        ...

    def get_all_by_camera(self, camera_id: int) -> list[SessionModel]:
        """Obtiene todas las sesiones históricas de una cámara específica."""
        ...


class SessionRepository:
    """Implementación concreta del repositorio de sesiones utilizando SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con la sesión activa de base de datos."""
        self.session = session

    def create(
        self,
        camera_id: int,
        started_at: datetime,
    ) -> SessionModel | None:
        """Crea, persiste y retorna una nueva sesión en la base de datos."""
        camera = self.session.get(CameraModel, camera_id)
        if camera is None or not camera.is_active:
            return None

        new_session = SessionModel(
            camera_id=camera_id,
            started_at=started_at,
            status="running",
        )
        self.session.add(new_session)
        self.session.commit()
        self.session.refresh(new_session)
        return new_session

    def get_by_id(self, session_id: int) -> SessionModel | None:
        """Busca y retorna un registro de sesión por su clave primaria, o None si no existe."""
        return self.session.get(SessionModel, session_id)

    def update(
        self,
        session_id: int,
        status: str,
        finished_at: datetime,
    ) -> SessionModel | None:
        """
        Modifica de manera selectiva los campos provistos de una sesión
        y persiste los cambios.
        """
        session = self.session.get(SessionModel, session_id)
        if session is None:
            return None

        session.status = status
        session.finished_at = finished_at

        self.session.commit()
        self.session.refresh(session)
        return session

    def get_all_by_camera(self, camera_id: int) -> list[SessionModel]:
        """Consulta las sesiones de una cámara, ordenadas por fecha."""
        stmt = (
            select(SessionModel)
            .where(SessionModel.camera_id == camera_id)
            .order_by(SessionModel.started_at.desc())
        )
        return list(self.session.scalars(stmt).all())
