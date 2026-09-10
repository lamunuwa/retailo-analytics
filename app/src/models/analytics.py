from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.src.core.db import Base


class DetectionEvent(Base):
    """Modelo SQLAlchemy para almacenar los eventos de detección analítica."""

    __tablename__ = "detection_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    camera_id: Mapped[int] = mapped_column(Integer, index=True)
    zone_name: Mapped[str] = mapped_column(String)
    people_count: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
