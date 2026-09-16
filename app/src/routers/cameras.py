from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.cameras import CameraModel
from app.src.repos.cameras import CameraRepository, CameraRepositoryProtocol
from app.src.schemas.cameras import CameraCreate, CameraRead, CameraUpdate

router = APIRouter(tags=["Cameras"])


def get_camera_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CameraRepositoryProtocol:
    """Construye el repositorio de camaras"""
    return CameraRepository(session=session)


@router.post(
    "/stores/{store_id}/cameras",
    response_model=CameraRead,
    status_code=status.HTTP_201_CREATED,
)
def create_camera(
    store_id: int,
    payload: CameraCreate,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    """Crea una camara para una tienda"""
    camera = repo.create(
        store_id=store_id,
        name=payload.name,
        source_type=payload.source_type,
        description=payload.description,
    )
    if camera is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return camera


@router.get("/stores/{store_id}/cameras", response_model=list[CameraRead])
def get_all_cameras(
    store_id: int,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> list[CameraModel]:
    """Obtiene las camaras activas de una tienda"""
    return repo.get_all_by_store(store_id=store_id)


@router.get("/cameras/{camera_id}", response_model=CameraRead)
def get_camera(
    camera_id: int,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    """Obtiene una camara por identificador"""
    camera = repo.get_by_id(camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camara no encontrada")
    return camera


@router.patch("/cameras/{camera_id}", response_model=CameraRead)
def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    """Actualiza una camara"""
    camera = repo.update(
        camera_id=camera_id,
        name=payload.name,
        description=payload.description,
        source_type=payload.source_type,
        is_active=payload.is_active,
    )
    if camera is None:
        raise HTTPException(status_code=404, detail="Camara no encontrada")
    return camera


@router.delete("/cameras/{camera_id}", response_model=CameraRead)
def delete_camera(
    camera_id: int,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    """Desactiva una camara"""
    camera = repo.delete(camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camara no encontrada")
    return camera
