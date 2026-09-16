import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.src.core.security import (
    create_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.src.models.auth import AuthSessionModel, UserModel
from app.src.repos.auth import AuthRepositoryProtocol


class EmailAlreadyRegisteredError(Exception):
    """Indica que un correo ya esta registrado."""


class InvalidCredentialsError(Exception):
    """Indica que las credenciales no son validas."""


class InactiveUserError(Exception):
    """Indica que una cuenta esta inactiva."""


class PasswordUnchangedError(Exception):
    """Indica que la contrasena nueva no cambio."""


@dataclass(frozen=True)
class AuthenticatedSession:
    """Agrupa una sesion valida y su usuario."""

    user: UserModel
    session: AuthSessionModel


@dataclass(frozen=True)
class IssuedSession:
    """Agrupa los datos de una sesion emitida."""

    user: UserModel
    token: str
    expires_at: datetime


class AuthService:
    """Coordina el registro y las sesiones de usuario."""

    def __init__(self, repository: AuthRepositoryProtocol) -> None:
        """Inicializa el servicio con un repositorio."""
        self.repository = repository

    def register(self, name: str, email: str, password: str) -> IssuedSession:
        """Registra un usuario y abre su primera sesion."""
        normalized_email = email.casefold()
        if self.repository.get_user_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError
        user = self.repository.create_user(
            name=name,
            email=normalized_email,
            password_hash=hash_password(password),
        )
        return self._issue_session(user)

    def login(self, email: str, password: str) -> IssuedSession:
        """Valida credenciales y abre una sesion."""
        user = self.repository.get_user_by_email(email.casefold())
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError
        if not user.is_active:
            raise InactiveUserError
        return self._issue_session(user)

    def authenticate(self, token: str) -> AuthenticatedSession:
        """Resuelve un token de acceso activo."""
        auth_session = self.repository.get_session(hash_session_token(token))
        if auth_session is None:
            raise InvalidCredentialsError
        expires_at = auth_session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            self.repository.delete_session(auth_session)
            raise InvalidCredentialsError
        if not auth_session.user.is_active:
            raise InactiveUserError
        return AuthenticatedSession(user=auth_session.user, session=auth_session)

    def change_password(
        self,
        authenticated: AuthenticatedSession,
        current_password: str,
        new_password: str,
    ) -> None:
        """Cambia la contrasena y cierra las otras sesiones."""
        if not verify_password(current_password, authenticated.user.password_hash):
            raise InvalidCredentialsError
        if current_password == new_password:
            raise PasswordUnchangedError
        self.repository.update_password(authenticated.user, hash_password(new_password))
        self.repository.delete_other_sessions(
            user_id=authenticated.user.id,
            session_id=authenticated.session.id,
        )

    def logout(self, authenticated: AuthenticatedSession) -> None:
        """Cierra la sesion actual."""
        self.repository.delete_session(authenticated.session)

    def _issue_session(self, user: UserModel) -> IssuedSession:
        """Emite y persiste una sesion opaca."""
        token = create_session_token()
        expires_at = datetime.now(UTC) + timedelta(days=self._session_days())
        self.repository.create_session(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=expires_at,
        )
        return IssuedSession(user=user, token=token, expires_at=expires_at)

    @staticmethod
    def _session_days() -> int:
        """Obtiene la duracion configurada de las sesiones."""
        try:
            return max(1, int(os.getenv("AUTH_SESSION_DAYS", "7")))
        except ValueError:
            return 7
