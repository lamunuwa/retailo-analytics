from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.src.models.cameras import CameraModel
from app.src.routers.cameras import (
    create_camera,
    delete_camera,
    get_all_cameras,
    get_camera,
    update_camera,
)
from app.src.schemas.cameras import CameraCreate, CameraUpdate


def test_create_camera_endpoint() -> None:
    """Verifica que el endpoint POST registre una cámara correctamente."""
    mock_repo = MagicMock()
    mock_repo.create.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara Pasillo",
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    response = create_camera(
        store_id=5,
        payload=CameraCreate.model_validate(
            {"name": "Cámara Pasillo", "source_type": "demo_video"}
        ),
        repo=mock_repo,
    )
    assert response.name == "Cámara Pasillo"
    assert response.source_type == "demo_video"

    # Valida que el repositorio haya recibido los datos exactos
    mock_repo.create.assert_called_once_with(
        store_id=5,
        name="Cámara Pasillo",
        source_type="demo_video",
        description=None,
    )


def test_list_cameras_endpoint() -> None:
    """Verifica que el endpoint GET liste las cámaras activas de una tienda."""
    mock_repo = MagicMock()
    mock_repo.get_all_by_store.return_value = [
        CameraModel(
            id=1,
            store_id=5,
            name="Cámara Pasillo",
            source_type="demo_video",
            is_active=True,
            created_at=datetime.now(UTC),
        )
    ]
    response = get_all_cameras(store_id=5, repo=mock_repo)
    assert len(response) == 1
    assert response[0].name == "Cámara Pasillo"

    mock_repo.get_all_by_store.assert_called_once_with(store_id=5)


def test_get_camera_by_id_endpoint() -> None:
    """Verifica que el endpoint GET obtenga una cámara específica por su ID."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara Principal",
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    response = get_camera(camera_id=1, repo=mock_repo)
    assert response.name == "Cámara Principal"

    mock_repo.get_by_id.assert_called_once_with(camera_id=1)


def test_get_camera_not_found_returns_404() -> None:
    """Verifica que se devuelva un error 404 si la cámara consultada no existe."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exception:
        get_camera(camera_id=999, repo=mock_repo)

    assert exception.value.status_code == 404
    assert exception.value.detail == "Camara no encontrada"


def test_update_camera_endpoint() -> None:
    """Verifica la actualización parcial (PATCH) de una cámara existente."""
    mock_repo = MagicMock()
    mock_repo.update.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara Actualizada",
        source_type="demo_video",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    response = update_camera(
        camera_id=1,
        payload=CameraUpdate.model_validate({"name": "Cámara Actualizada"}),
        repo=mock_repo,
    )
    assert response.name == "Cámara Actualizada"

    # Confirma que el repositorio procesó los valores esperados
    mock_repo.update.assert_called_once_with(
        camera_id=1,
        name="Cámara Actualizada",
        description=None,
        source_type=None,
        is_active=None,
    )


def test_soft_delete_camera_endpoint() -> None:
    """Verifica el borrado lógico (DELETE) cambiando el estado is_active a False."""
    mock_repo = MagicMock()
    mock_repo.delete.return_value = CameraModel(
        id=1,
        store_id=5,
        name="Cámara a borrar",
        source_type="demo_video",
        is_active=False,
        created_at=datetime.now(UTC),
    )
    response = delete_camera(camera_id=1, repo=mock_repo)
    assert response.is_active is False

    mock_repo.delete.assert_called_once_with(camera_id=1)
