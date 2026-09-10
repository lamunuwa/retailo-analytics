from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.sessions import SessionModel
from app.src.repos.sessions import SessionRepository, SessionRepositoryProtocol
from app.src.schemas.sessions import SessionCreate, SessionRead, SessionUpdate

router = APIRouter(tags=["Sessions"])


def get_session_repository(
    session: Annotated[Session, Depends(get_db)],
) -> SessionRepositoryProtocol:
    """Inyecta la instancia del repositorio de sesiones."""
    return SessionRepository(session=session)


@router.post(
    "/cameras/{camera_id}/sessions",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    camera_id: int,
    payload: SessionCreate,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
) -> SessionModel:
    """Registra una nueva sesión de video para una cámara."""
    session = repo.create(
        camera_id=camera_id,
        started_at=payload.started_at,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return session


@router.get("/sessions/{session_id}", response_model=SessionRead)
def get_session(
    session_id: int,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
) -> SessionModel:
    """Obtiene el estado de una sesión por su ID."""
    session = repo.get_by_id(session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/sessions/{session_id}", response_model=SessionRead)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
) -> SessionModel:
    """Actualiza el estado de una sesión (típicamente al finalizar)."""
    session = repo.get_by_id(session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "running":
        raise HTTPException(status_code=409, detail="Session is already finalized")
    if payload.finished_at < session.started_at:
        raise HTTPException(
            status_code=422,
            detail="finished_at must be later than started_at",
        )

    updated_session = repo.update(
        session_id=session_id,
        status=payload.status,
        finished_at=payload.finished_at,
    )
    if updated_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated_session


@router.get("/cameras/{camera_id}/sessions", response_model=list[SessionRead])
def list_sessions(
    camera_id: int,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
) -> list[SessionModel]:
    """Obtiene el historial de sesiones de una cámara."""
    return repo.get_all_by_camera(camera_id=camera_id)
