from typing import Annotated
from fastapi import APIRouter, Depends, status
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