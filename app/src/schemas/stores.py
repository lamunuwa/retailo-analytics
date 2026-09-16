from pydantic import BaseModel, ConfigDict, Field, model_validator


class StoreCreate(BaseModel):
    """Valida la creacion de una tienda"""

    name: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class StoreUpdate(BaseModel):
    """Valida la actualizacion de una tienda"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "StoreUpdate":
        """Valida que exista al menos un cambio"""
        if not self.model_fields_set:
            raise ValueError("Se debe proporcionar al menos un campo para actualizar")
        return self


class StoreResponse(StoreCreate):
    """Representa la respuesta de una tienda"""

    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
