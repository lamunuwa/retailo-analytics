from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.stores import StoreModel
from app.src.repos.stores import StoreRepository, StoreRepositoryProtocol
from app.src.schemas.stores import StoreCreate, StoreResponse, StoreUpdate

router = APIRouter(prefix="/stores", tags=["Stores"])


def get_store_repository(
    session: Annotated[Session, Depends(get_db)],
) -> StoreRepositoryProtocol:
    """Construye el repositorio de tiendas"""
    return StoreRepository(session=session)


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    """Crea una tienda"""
    return repo.create(name=payload.name)


@router.get("", response_model=list[StoreResponse])
def get_all_stores(
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> list[StoreModel]:
    """Obtiene las tiendas activas"""
    return repo.get_all()


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    """Obtiene una tienda por identificador"""
    store = repo.get_by_id(store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    payload: StoreUpdate,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    """Actualiza una tienda"""
    store = repo.update(store_id=store_id, name=payload.name, is_active=payload.is_active)
    if store is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.delete("/{store_id}", response_model=StoreResponse)
def delete_store(
    store_id: int,
    repo: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
) -> StoreModel:
    """Desactiva una tienda"""
    store = repo.delete(store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store
