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