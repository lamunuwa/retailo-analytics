from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.cameras import CameraModel
from app.src.models.sessions import SessionModel


class SessionRepositoryProtocol(Protocol):
    """Define las operaciones de sesiones"""

    def create(
        self,
        camera_id: int,
        started_at: datetime,
    ) -> SessionModel | None:
        """Crea una sesion para una camara"""
        ...

    def get_by_id(self, session_id: int) -> SessionModel | None:
        """Obtiene una sesion por identificador"""
        ...

    def update(
        self,
        session_id: int,
        status: str,
        finished_at: datetime,
    ) -> SessionModel | None:
        """Actualiza una sesion"""
        ...

    def get_all_by_camera(
        self,
        camera_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SessionModel]:
        """Obtiene las sesiones de una camara"""
        ...


class SessionRepository:
    """Gestiona la persistencia de sesiones"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def create(
        self,
        camera_id: int,
        started_at: datetime,
    ) -> SessionModel | None:
        """Crea una sesion para una camara"""
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
        """Obtiene una sesion por identificador"""
        return self.session.get(SessionModel, session_id)

    def update(
        self,
        session_id: int,
        status: str,
        finished_at: datetime,
    ) -> SessionModel | None:
        """Actualiza una sesion"""
        session = self.session.get(SessionModel, session_id)
        if session is None:
            return None

        session.status = status
        session.finished_at = finished_at

        self.session.commit()
        self.session.refresh(session)
        return session

    def get_all_by_camera(
        self,
        camera_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SessionModel]:
        """Obtiene las sesiones de una camara"""
        stmt = (
            select(SessionModel)
            .where(SessionModel.camera_id == camera_id)
            .order_by(SessionModel.started_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
