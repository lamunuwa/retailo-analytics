from collections.abc import Sequence

from app.src.models.analytics import DetectionEvent
from app.src.repos.analytics import AnalyticsRepository
from app.src.schemas.analytics import DetectionEventCreate


class AnalyticsService:
    """Capa de lógica de negocio para analítica y detecciones."""

    def __init__(self, repo: AnalyticsRepository) -> None:
        self.repo = repo

    def register_detection(self, event_data: DetectionEventCreate) -> DetectionEvent:
        """Procesa y guarda un nuevo evento de detección."""
        return self.repo.create(event_data)

    def get_detections(self) -> Sequence[DetectionEvent]:
        """Retorna el listado de eventos registrados."""
        return self.repo.get_all()