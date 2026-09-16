from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.sessions import SessionModel
from app.src.repos.sessions import SessionRepository, SessionRepositoryProtocol
from app.src.schemas.sessions import SessionCreate, SessionRead, SessionUpdate

router = APIRouter(tags=["Sessions"])


def get_session_repository(
    session: Annotated[Session, Depends(get_db)],
) -> SessionRepositoryProtocol:
    """Construye el repositorio de sesiones"""
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
    """Crea una sesion para una camara"""
    session = repo.create(
        camera_id=camera_id,
        started_at=payload.started_at,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Camara no encontrada")
    return session


@router.get("/sessions/{session_id}", response_model=SessionRead)
def get_session(
    session_id: int,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
) -> SessionModel:
    """Obtiene una sesion por identificador"""
    session = repo.get_by_id(session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    return session


@router.patch("/sessions/{session_id}", response_model=SessionRead)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
) -> SessionModel:
    """Actualiza una sesion"""
    session = repo.get_by_id(session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    if session.status != "running":
        raise HTTPException(status_code=409, detail="La sesion ya fue finalizada")
    if payload.finished_at < session.started_at:
        raise HTTPException(
            status_code=422,
            detail="finished_at debe ser posterior a started_at",
        )

    updated_session = repo.update(
        session_id=session_id,
        status=payload.status,
        finished_at=payload.finished_at,
    )
    if updated_session is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    return updated_session


@router.get("/cameras/{camera_id}/sessions", response_model=list[SessionRead])
def get_all_sessions(
    camera_id: int,
    repo: Annotated[SessionRepositoryProtocol, Depends(get_session_repository)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SessionModel]:
    """Obtiene las sesiones de una camara"""
    return repo.get_all_by_camera(camera_id=camera_id, limit=limit, offset=offset)
