from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.src.models.analytics import DetectionEvent
from app.src.schemas.analytics import DetectionEventCreate, DetectionFilters


class AnalyticsRepository:
    """Maneja las operaciones de lectura y escritura en la base de datos para analítica."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event_data: DetectionEventCreate) -> DetectionEvent:
        """Persiste un nuevo evento de detección en la base de datos."""
        db_event = DetectionEvent(
            camera_id=event_data.camera_id,
            zone_name=event_data.zone_name,
            people_count=event_data.people_count,
            timestamp=event_data.timestamp,
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_all(self, filters: DetectionFilters | None = None) -> Sequence[DetectionEvent]:
        """Obtiene una lista de eventos con filtros opcionales y paginación."""
        query = self.db.query(DetectionEvent)

        if filters:
            if filters.camera_id is not None:
                query = query.filter(DetectionEvent.camera_id == filters.camera_id)
            if filters.zone_name is not None:
                query = query.filter(DetectionEvent.zone_name == filters.zone_name)
            if filters.start_date is not None:
                query = query.filter(DetectionEvent.timestamp >= filters.start_date)
            if filters.end_date is not None:
                query = query.filter(DetectionEvent.timestamp <= filters.end_date)

            query = query.order_by(DetectionEvent.timestamp.desc(), DetectionEvent.id.desc())
            query = query.offset(filters.offset).limit(filters.limit)
        else:
            query = query.order_by(DetectionEvent.timestamp.desc(), DetectionEvent.id.desc())

        return query.all()