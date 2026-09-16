from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.core.db import get_db
from app.src.models.zones import ZoneModel
from app.src.repos.zones import ZoneRepository, ZoneRepositoryProtocol
from app.src.schemas.zones import ZoneCreate, ZoneRead, ZoneUpdate

router = APIRouter(tags=["Zones"])


def get_zone_repository(
    session: Annotated[Session, Depends(get_db)],
) -> ZoneRepositoryProtocol:
    """Construye el repositorio de zonas"""
    return ZoneRepository(session)


@router.post(
    "/cameras/{camera_id}/zones",
    response_model=ZoneRead,
    status_code=status.HTTP_201_CREATED,
)
def create_zone(
    camera_id: int,
    payload: ZoneCreate,
    repo: Annotated[ZoneRepositoryProtocol, Depends(get_zone_repository)],
) -> ZoneModel:
    """Crea una zona para una camara"""
    camera = repo.get_camera_by_id(camera_id)
    if camera is None or not camera.is_active:
        raise HTTPException(status_code=404, detail="Camara no encontrada")
    existing_zone = repo.get_by_name(camera_id, payload.name)
    if existing_zone is not None and existing_zone.is_active:
        raise HTTPException(
            status_code=409,
            detail="El nombre de la zona ya existe para esta camara",
        )
    if existing_zone is not None:
        return repo.update(
            existing_zone,
            {
                "zone_type": payload.zone_type,
                "points": [point.model_dump() for point in payload.points],
                "is_active": True,
            },
        )
    return repo.create(
        camera_id=camera_id,
        name=payload.name,
        zone_type=payload.zone_type,
        points=[point.model_dump() for point in payload.points],
    )


@router.get("/cameras/{camera_id}/zones", response_model=list[ZoneRead])
def get_all_zones(
    camera_id: int,
    repo: Annotated[ZoneRepositoryProtocol, Depends(get_zone_repository)],
) -> list[ZoneModel]:
    """Obtiene las zonas de una camara"""
    camera = repo.get_camera_by_id(camera_id)
    if camera is None or not camera.is_active:
        raise HTTPException(status_code=404, detail="Camara no encontrada")
    return repo.get_all_by_camera(camera_id)


@router.get("/zones/{zone_id}", response_model=ZoneRead)
def get_zone(
    zone_id: int,
    repo: Annotated[ZoneRepositoryProtocol, Depends(get_zone_repository)],
) -> ZoneModel:
    """Obtiene una zona por identificador"""
    zone = repo.get_by_id(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return zone


@router.patch("/zones/{zone_id}", response_model=ZoneRead)
def update_zone(
    zone_id: int,
    payload: ZoneUpdate,
    repo: Annotated[ZoneRepositoryProtocol, Depends(get_zone_repository)],
) -> ZoneModel:
    """Actualiza una zona"""
    zone = repo.get_by_id(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and repo.get_by_name(zone.camera_id, changes["name"], zone.id):
        raise HTTPException(
            status_code=409,
            detail="El nombre de la zona ya existe para esta camara",
        )
    if "points" in changes:
        changes["points"] = [point.model_dump() for point in payload.points or []]
    return repo.update(zone, changes)


@router.delete("/zones/{zone_id}", response_model=ZoneRead)
def delete_zone(
    zone_id: int,
    repo: Annotated[ZoneRepositoryProtocol, Depends(get_zone_repository)],
) -> ZoneModel:
    """Desactiva una zona"""
    zone = repo.get_by_id(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return repo.delete(zone)
