from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.src.core.db import Base


class VideoResultModel(Base):
    """Representa el resultado de una sesion de video"""

    __tablename__ = "video_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id"), unique=True, index=True, nullable=False
    )
    processed_frames: Mapped[int] = mapped_column(Integer, nullable=False)
    elapsed_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    detected_people: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    zone_metrics: Mapped[list["ZoneMetricModel"]] = relationship(
        back_populates="video_result",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ZoneMetricModel.zone_id",
    )


class ZoneMetricModel(Base):
    """Representa las metricas de una zona"""

    __tablename__ = "zone_metrics"
    __table_args__ = (
        UniqueConstraint("video_result_id", "zone_id", name="uq_zone_metrics_result_zone"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_result_id: Mapped[int] = mapped_column(
        ForeignKey("video_results.id", ondelete="CASCADE"), index=True, nullable=False
    )
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), index=True, nullable=False)
    visits: Mapped[int] = mapped_column(Integer, nullable=False)
    dwell_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    traffic_share: Mapped[float] = mapped_column(Float, nullable=False)
    video_result: Mapped[VideoResultModel] = relationship(back_populates="zone_metrics")
