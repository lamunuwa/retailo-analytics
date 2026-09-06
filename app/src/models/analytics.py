from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.src.core.db import Base


class DetectionEvent(Base):
    """Modelo SQLAlchemy para eventos de detección."""

    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, nullable=False, index=True)
    zone_name = Column(String, nullable=False)
    people_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
