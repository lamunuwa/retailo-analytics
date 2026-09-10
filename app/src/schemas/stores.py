from pydantic import BaseModel, ConfigDict, Field, model_validator


class StoreCreate(BaseModel):
    name: str = Field(min_length=1)


class StoreUpdate(BaseModel):
    """Campos modificables de una tienda mediante PATCH."""

    name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "StoreUpdate":
        if not self.model_fields_set:
            raise ValueError("Se debe proporcionar al menos un campo para actualizar")
        return self


class StoreResponse(StoreCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
