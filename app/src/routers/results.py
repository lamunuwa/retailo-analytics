from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.results import VideoResultModel
from app.src.repos.results import VideoResultRepository, VideoResultRepositoryProtocol
from app.src.schemas.results import VideoResultCreate, VideoResultRead

router = APIRouter(tags=["Results"])


def get_result_repository(
    session: Annotated[Session, Depends(get_db)],
) -> VideoResultRepositoryProtocol:
    """Construye el repositorio de resultados"""
    return VideoResultRepository(session)


@router.post(
    "/sessions/{session_id}/video-results",
    response_model=VideoResultRead,
    status_code=status.HTTP_201_CREATED,
)
def create_video_result(
    session_id: int,
    payload: VideoResultCreate,
    repo: Annotated[VideoResultRepositoryProtocol, Depends(get_result_repository)],
) -> VideoResultModel:
    """Crea el resultado de una sesion de video"""
    video_session = repo.get_session_by_id(session_id)
    if video_session is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    if repo.get_by_session_id(session_id) is not None:
        raise HTTPException(status_code=409, detail="El resultado de video ya existe")
    if video_session.status != "running":
        raise HTTPException(status_code=409, detail="La sesion ya fue finalizada")
    requested_zone_ids = {metric.zone_id for metric in payload.zone_metrics}
    valid_zone_ids = repo.get_zone_ids_by_camera(video_session.camera_id, requested_zone_ids)
    if valid_zone_ids != requested_zone_ids:
        raise HTTPException(
            status_code=422,
            detail="Cada zone_id debe pertenecer a la camara de la sesion",
        )
    return repo.create(video_session, payload)


@router.get("/sessions/{session_id}/video-results", response_model=VideoResultRead)
def get_video_result(
    session_id: int,
    repo: Annotated[VideoResultRepositoryProtocol, Depends(get_result_repository)],
) -> VideoResultModel:
    """Obtiene el resultado de una sesion de video"""
    if repo.get_session_by_id(session_id) is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    result = repo.get_by_session_id(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Resultado de video no encontrado")
    return result
