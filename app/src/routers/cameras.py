from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.repos.cameras import CameraRepository, CameraRepositoryProtocol

router = APIRouter(tags=["Cameras"])

def get_camera_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CameraRepositoryProtocol:
    return CameraRepository(session=session)