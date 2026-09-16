from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.sales import SalesRecordModel
from app.src.repos.sales import SalesRepository, SalesRepositoryProtocol
from app.src.schemas.sales import SalesRecordCreate, SalesRecordRead

router = APIRouter(tags=["Sales"])


def get_sales_repository(
    session: Annotated[Session, Depends(get_db)],
) -> SalesRepositoryProtocol:
    """Construye el repositorio de ventas"""
    return SalesRepository(session)


@router.post(
    "/stores/{store_id}/sales",
    response_model=SalesRecordRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sales_record(
    store_id: int,
    payload: SalesRecordCreate,
    repo: Annotated[SalesRepositoryProtocol, Depends(get_sales_repository)],
) -> SalesRecordModel:
    """Crea un registro de venta"""
    store = repo.get_store_by_id(store_id)
    if store is None or not store.is_active:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    if repo.get_zone_by_store(store_id, payload.zone_id) is None:
        raise HTTPException(status_code=422, detail="zone_id debe pertenecer a la tienda")
    return repo.create(store_id, payload)


@router.get("/stores/{store_id}/sales", response_model=list[SalesRecordRead])
def get_all_sales_records(
    store_id: int,
    repo: Annotated[SalesRepositoryProtocol, Depends(get_sales_repository)],
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
) -> list[SalesRecordModel]:
    """Obtiene los registros de venta de una tienda"""
    store = repo.get_store_by_id(store_id)
    if store is None or not store.is_active:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date no debe ser posterior a end_date",
        )
    return repo.get_all_by_store(store_id, start_date, end_date)
