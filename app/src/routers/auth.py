from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.repos.auth import AuthRepository
from app.src.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.src.services.auth import (
    AuthenticatedSession,
    AuthService,
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
    IssuedSession,
    PasswordUnchangedError,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: Annotated[Session, Depends(get_db)]) -> AuthService:
    """Construye el servicio de autenticacion."""
    return AuthService(repository=AuthRepository(session=session))


def get_current_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticatedSession:
    """Valida el token Bearer de la peticion."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion no valida o vencida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return service.authenticate(credentials.credentials)
    except InvalidCredentialsError as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion no valida o vencida",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exception
    except InactiveUserError as exception:
        raise HTTPException(status_code=403, detail="La cuenta esta inactiva") from exception


def _auth_response(issued: IssuedSession) -> AuthResponse:
    """Construye la respuesta de una sesion emitida."""
    return AuthResponse(
        access_token=issued.token,
        expires_at=issued.expires_at,
        user=UserResponse.model_validate(issued.user),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthResponse:
    """Registra una cuenta e inicia su sesion."""
    try:
        return _auth_response(service.register(payload.name, payload.email, payload.password))
    except (EmailAlreadyRegisteredError, IntegrityError) as exception:
        raise HTTPException(status_code=409, detail="El correo ya esta registrado") from exception


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthResponse:
    """Inicia una sesion con correo y contrasena."""
    try:
        return _auth_response(service.login(payload.email, payload.password))
    except InvalidCredentialsError as exception:
        raise HTTPException(
            status_code=401, detail="Correo o contrasena incorrectos"
        ) from exception
    except InactiveUserError as exception:
        raise HTTPException(status_code=403, detail="La cuenta esta inactiva") from exception


@router.get("/me", response_model=UserResponse)
def get_me(
    authenticated: Annotated[AuthenticatedSession, Depends(get_current_session)],
) -> UserResponse:
    """Devuelve el usuario de la sesion actual."""
    return UserResponse.model_validate(authenticated.user)


@router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    authenticated: Annotated[AuthenticatedSession, Depends(get_current_session)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    """Cambia la contrasena del usuario autenticado."""
    try:
        service.change_password(
            authenticated=authenticated,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except InvalidCredentialsError as exception:
        raise HTTPException(
            status_code=400, detail="La contrasena actual es incorrecta"
        ) from exception
    except PasswordUnchangedError as exception:
        raise HTTPException(
            status_code=400, detail="La contrasena nueva debe ser diferente"
        ) from exception
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    authenticated: Annotated[AuthenticatedSession, Depends(get_current_session)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    """Cierra la sesion actual."""
    service.logout(authenticated)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
