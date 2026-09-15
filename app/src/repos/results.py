from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.src.models.results import VideoResultModel, ZoneMetricModel
from app.src.models.sessions import SessionModel
from app.src.models.zones import ZoneModel
from app.src.schemas.results import VideoResultCreate


class VideoResultRepositoryProtocol(Protocol):
    """Define las operaciones de resultados de video"""

    def get_session_by_id(self, session_id: int) -> SessionModel | None:
        """Obtiene una sesion por identificador"""
        ...

    def get_by_session_id(self, session_id: int) -> VideoResultModel | None:
        """Obtiene el resultado de una sesion"""
        ...

    def get_zone_ids_by_camera(self, camera_id: int, zone_ids: set[int]) -> set[int]:
        """Obtiene los identificadores validos de zonas"""
        ...

    def create(self, session: SessionModel, payload: VideoResultCreate) -> VideoResultModel:
        """Crea un resultado de video"""
        ...


class VideoResultRepository:
    """Gestiona la persistencia de resultados de video"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def get_session_by_id(self, session_id: int) -> SessionModel | None:
        """Obtiene una sesion por identificador"""
        return self.session.get(SessionModel, session_id)

    def get_by_session_id(self, session_id: int) -> VideoResultModel | None:
        """Obtiene el resultado de una sesion"""
        stmt = (
            select(VideoResultModel)
            .options(selectinload(VideoResultModel.zone_metrics))
            .where(VideoResultModel.session_id == session_id)
        )
        return self.session.scalar(stmt)

    def get_zone_ids_by_camera(self, camera_id: int, zone_ids: set[int]) -> set[int]:
        """Obtiene los identificadores validos de zonas"""
        if not zone_ids:
            return set()
        stmt = select(ZoneModel.id).where(
            ZoneModel.camera_id == camera_id,
            ZoneModel.id.in_(zone_ids),
        )
        return set(self.session.scalars(stmt).all())

    def create(self, session: SessionModel, payload: VideoResultCreate) -> VideoResultModel:
        """Crea un resultado de video"""
        result = VideoResultModel(
            session_id=session.id,
            processed_frames=payload.processed_frames,
            elapsed_seconds=payload.elapsed_seconds,
            detected_people=payload.detected_people,
            started_at=payload.started_at,
            finished_at=payload.finished_at,
            zone_metrics=[
                ZoneMetricModel(
                    zone_id=metric.zone_id,
                    visits=metric.visits,
                    dwell_seconds=metric.dwell_seconds,
                    traffic_share=metric.traffic_share,
                )
                for metric in payload.zone_metrics
            ],
        )
        session.status = "completed"
        session.finished_at = payload.finished_at
        self.session.add(result)
        self.session.commit()
        return self.get_by_session_id(session.id) or result
