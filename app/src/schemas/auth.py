import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterRequest(BaseModel):
    """Valida el registro de una cuenta."""

    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normaliza y valida un correo sencillo."""
        normalized = value.casefold()
        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("El correo no tiene un formato valido")
        return normalized


class LoginRequest(BaseModel):
    """Valida las credenciales de acceso."""

    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normaliza el correo de acceso."""
        return value.casefold()


class ChangePasswordRequest(BaseModel):
    """Valida el cambio de contrasena."""

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)

    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    """Expone los datos publicos de una cuenta."""

    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """Expone una sesion nueva y su usuario."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse
