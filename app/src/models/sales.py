from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.src.core.db import Base


class SalesRecordModel(Base):
    """Representa una venta agregada por zona"""

    __tablename__ = "sales_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True, nullable=False)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
