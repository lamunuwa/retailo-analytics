from datetime import UTC, datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class SalesRecordCreate(BaseModel):
    """Valida un registro de venta"""

    zone_id: int = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    units_sold: int = Field(ge=0)
    revenue: float = Field(ge=0)
    recorded_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SalesRecordRead(SalesRecordCreate):
    """Representa la respuesta de una venta"""

    id: int
    store_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
