from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.src.models.analytics import DetectionEvent
from app.src.schemas.analytics import DetectionEventCreate, DetectionFilters


class AnalyticsRepository:
    """Capa de acceso a datos para eventos de analítica."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event_data: DetectionEventCreate) -> DetectionEvent:
        db_event = DetectionEvent(**event_data.model_dump())
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_all(self, filters: DetectionFilters | None = None) -> Sequence[DetectionEvent]:
        """Obtiene detecciones aplicando filtros y paginación."""
        query = self.db.query(DetectionEvent)
        if filters is not None:
            if filters.camera_id is not None:
                query = query.filter(DetectionEvent.camera_id == filters.camera_id)
            if filters.zone_name is not None:
                query = query.filter(DetectionEvent.zone_name == filters.zone_name)
            if filters.start_date is not None:
                query = query.filter(DetectionEvent.timestamp >= filters.start_date)
            if filters.end_date is not None:
                query = query.filter(DetectionEvent.timestamp <= filters.end_date)
            query = query.offset(filters.offset).limit(filters.limit)
        return query.order_by(DetectionEvent.timestamp.desc(), DetectionEvent.id.desc())
