from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.stores import StoreModel
from app.src.repos.stores import StoreRepository, StoreRepositoryProtocol
from app.src.schemas.stores import StoreCreate, StoreResponse

router = APIRouter(prefix="/stores", tags=["Stores"])


def get_store_repository(
    session: Annotated[Session, Depends(get_db)],
) -> StoreRepositoryProtocol:
    return StoreRepository(session=session)


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    return repo.create(name=payload.name)


@router.get("/", response_model=list[StoreResponse])
def list_stores(
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> list[StoreModel]:
    return repo.get_all_active()


@router.delete("/{store_id}", response_model=StoreResponse)
def soft_delete_store(
    store_id: int,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    store = repo.soft_delete(store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    payload: StoreCreate,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    store = repo.update(store_id=store_id, name=payload.name)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store