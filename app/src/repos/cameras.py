from typing import Protocol
from sqlalchemy.orm import Session
from app.src.models.cameras import CameraModel

class CameraRepositoryProtocol(Protocol):
    pass  # Aquí definirás las firmas de create, get_all, update, soft_delete

class CameraRepository:
    def __init__(self, session: Session) -> None:
        self.session = session