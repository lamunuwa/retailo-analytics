from datetime import datetime
from typing import Protocol

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.src.models.auth import AuthSessionModel, UserModel


class AuthRepositoryProtocol(Protocol):
    """Define las operaciones de autenticacion."""

    def get_user_by_email(self, email: str) -> UserModel | None:
        """Busca un usuario por correo."""
        ...

    def create_user(self, name: str, email: str, password_hash: str) -> UserModel:
        """Crea una cuenta de usuario."""
        ...

    def create_session(
        self, user_id: int, token_hash: str, expires_at: datetime
    ) -> AuthSessionModel:
        """Crea una sesion de usuario."""
        ...

    def get_session(self, token_hash: str) -> AuthSessionModel | None:
        """Busca una sesion por su huella."""
        ...

    def update_password(self, user: UserModel, password_hash: str) -> None:
        """Actualiza la contrasena de un usuario."""
        ...

    def delete_session(self, session: AuthSessionModel) -> None:
        """Elimina una sesion."""
        ...

    def delete_other_sessions(self, user_id: int, session_id: int) -> None:
        """Elimina las otras sesiones de un usuario."""
        ...


class AuthRepository:
    """Gestiona la persistencia de autenticacion."""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion."""
        self.session = session

    def get_user_by_email(self, email: str) -> UserModel | None:
        """Busca un usuario por correo normalizado."""
        return self.session.scalar(select(UserModel).where(UserModel.email == email.casefold()))

    def create_user(self, name: str, email: str, password_hash: str) -> UserModel:
        """Crea una cuenta de usuario."""
        user = UserModel(name=name, email=email.casefold(), password_hash=password_hash)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_session(
        self, user_id: int, token_hash: str, expires_at: datetime
    ) -> AuthSessionModel:
        """Crea una sesion de usuario."""
        auth_session = AuthSessionModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(auth_session)
        self.session.commit()
        self.session.refresh(auth_session)
        return auth_session

    def get_session(self, token_hash: str) -> AuthSessionModel | None:
        """Busca una sesion por su huella."""
        return self.session.scalar(
            select(AuthSessionModel).where(AuthSessionModel.token_hash == token_hash)
        )

    def update_password(self, user: UserModel, password_hash: str) -> None:
        """Actualiza la contrasena de un usuario."""
        user.password_hash = password_hash
        self.session.commit()

    def delete_session(self, session: AuthSessionModel) -> None:
        """Elimina una sesion."""
        self.session.delete(session)
        self.session.commit()

    def delete_other_sessions(self, user_id: int, session_id: int) -> None:
        """Elimina las otras sesiones de un usuario."""
        statement = delete(AuthSessionModel).where(
            AuthSessionModel.user_id == user_id,
            AuthSessionModel.id != session_id,
        )
        self.session.execute(statement)
        self.session.commit()
