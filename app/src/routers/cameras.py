from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.cameras import CameraModel
from app.src.repos.cameras import CameraRepository, CameraRepositoryProtocol
from app.src.schemas.cameras import CameraCreate, CameraRead

router = APIRouter(tags=["Cameras"])

def get_camera_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CameraRepositoryProtocol:
    return CameraRepository(session=session)

@router.post("/stores/{store_id}/cameras", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
def create_camera(
    store_id: int,
    payload: CameraCreate,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    return repo.create(
        store_id=store_id,
        name=payload.name,
        source_type=payload.source_type,
        description=payload.description,
    )

@router.get("/stores/{store_id}/cameras", response_model=list[CameraRead])
def list_cameras(
    store_id: int,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> list[CameraModel]:
    return repo.get_all_by_store(store_id=store_id)

@router.get("/cameras/{camera_id}", response_model=CameraRead)
def get_camera(
    camera_id: int,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    camera = repo.get_by_id(camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

from app.src.schemas.cameras import CameraCreate, CameraRead, CameraUpdate

@router.patch("/cameras/{camera_id}", response_model=CameraRead)
#Agrega la importación de CameraUpdate y el endpoint
def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    repo: Annotated[CameraRepositoryProtocol, Depends(get_camera_repository)],
) -> CameraModel:
    camera = repo.update(
        camera_id=camera_id,
        name=payload.name,
        description=payload.description,
        source_type=payload.source_type,
        is_active=payload.is_active,
    )
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera