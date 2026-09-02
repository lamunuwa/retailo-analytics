from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.stores import StoreModel
from app.src.repos.stores import StoreRepository
from app.src.schemas.stores import StoreCreate, StoreResponse

router = APIRouter(prefix="/stores", tags=["Stores"])


def get_store_repository(
    session: Annotated[Session, Depends(get_db)],
) -> StoreRepository:
    return StoreRepository(session=session)


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    repo: Annotated[StoreRepository, Depends(get_store_repository)],
) -> StoreModel:
    return repo.create(name=payload.name)