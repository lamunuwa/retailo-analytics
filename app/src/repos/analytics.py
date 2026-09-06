from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.src.models.analytics import DetectionEvent
from app.src.schemas.analytics import DetectionEventCreate


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

    def get_all(self) -> Sequence[DetectionEvent]:
        """Obtiene todos los eventos de detección registrados."""
        return self.db.query(DetectionEvent).all()