from datetime import UTC, datetime
from unittest.mock import ANY, MagicMock

import pytest
from fastapi import HTTPException

from app.src.models.sessions import SessionModel
from app.src.repos.sessions import SessionRepository
from app.src.routers.sessions import (
    create_session,
    get_session,
    list_sessions,
    update_session,
)
from app.src.schemas.sessions import SessionCreate, SessionUpdate


def test_create_session_endpoint() -> None:
    """Verifica que el endpoint POST registre una sesión correctamente."""
    mock_repo = MagicMock()
    mock_repo.create.return_value = SessionModel(
        id=1,
        camera_id=5,
        status="running",
        started_at=datetime.now(UTC),
        finished_at=None,
        created_at=datetime.now(UTC),
    )
    response = create_session(
        camera_id=5,
        payload=SessionCreate.model_validate({"started_at": datetime.now(UTC).isoformat()}),
        repo=mock_repo,
    )
    assert response.status == "running"
    assert response.camera_id == 5

    mock_repo.create.assert_called_once_with(camera_id=5, started_at=ANY)


def test_create_session_rejects_an_unknown_camera() -> None:
    """Verifica que no se creen sesiones sin una cámara registrada."""
    mock_repo = MagicMock()
    mock_repo.create.return_value = None

    with pytest.raises(HTTPException) as exception:
        create_session(camera_id=999, payload=SessionCreate(), repo=mock_repo)

    assert exception.value.status_code == 404
    assert exception.value.detail == "Camera not found"


def test_get_session_by_id_endpoint() -> None:
    """Verifica que el endpoint GET obtenga una sesión específica por su ID."""
    mock_repo = MagicMock()
    now = datetime.now(UTC)
    mock_repo.get_by_id.return_value = SessionModel(
        id=1,
        camera_id=5,
        status="running",
        started_at=now,
        finished_at=None,
        created_at=now,
    )
    response = get_session(session_id=1, repo=mock_repo)
    assert response.status == "running"
    assert response.id == 1

    mock_repo.get_by_id.assert_called_once_with(session_id=1)


def test_get_session_not_found_returns_404() -> None:
    """Verifica que se devuelva un error 404 si la sesión no existe."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exception:
        get_session(session_id=999, repo=mock_repo)

    assert exception.value.status_code == 404
    assert exception.value.detail == "Session not found"


def test_update_session_endpoint() -> None:
    """Verifica la actualización (PATCH) de una sesión existente."""
    mock_repo = MagicMock()
    now = datetime.now(UTC)
    mock_repo.get_by_id.return_value = SessionModel(
        id=1,
        camera_id=5,
        status="running",
        started_at=now,
        finished_at=None,
        created_at=now,
    )
    mock_repo.update.return_value = SessionModel(
        id=1,
        camera_id=5,
        status="completed",
        started_at=now,
        finished_at=now,
        created_at=now,
    )
    response = update_session(
        session_id=1,
        payload=SessionUpdate.model_validate(
            {
                "status": "completed",
                "finished_at": now.isoformat(),
            }
        ),
        repo=mock_repo,
    )
    assert response.status == "completed"
    assert response.finished_at is not None

    mock_repo.update.assert_called_once_with(
        session_id=1,
        status="completed",
        finished_at=now,
    )


def test_update_session_not_found_returns_404() -> None:
    """Verifica que se devuelva un error 404 si se intenta actualizar una sesión inexistente."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exception:
        update_session(
            session_id=999,
            payload=SessionUpdate.model_validate(
                {"status": "completed", "finished_at": datetime.now(UTC).isoformat()}
            ),
            repo=mock_repo,
        )

    assert exception.value.status_code == 404


def test_update_session_rejects_a_finalized_session() -> None:
    """Una sesión completada o fallida no puede regresar a otro estado."""
    mock_repo = MagicMock()
    now = datetime.now(UTC)
    mock_repo.get_by_id.return_value = SessionModel(
        id=1,
        camera_id=5,
        status="completed",
        started_at=now,
        finished_at=now,
        created_at=now,
    )

    with pytest.raises(HTTPException) as exception:
        update_session(
            session_id=1,
            payload=SessionUpdate(status="failed", finished_at=now),
            repo=mock_repo,
        )

    assert exception.value.status_code == 409
    mock_repo.update.assert_not_called()


def test_update_session_rejects_a_finish_before_the_start() -> None:
    """La marca de finalización no puede ser anterior al inicio."""
    mock_repo = MagicMock()
    started_at = datetime(2026, 9, 9, 12, 0, tzinfo=UTC)
    mock_repo.get_by_id.return_value = SessionModel(
        id=1,
        camera_id=5,
        status="running",
        started_at=started_at,
        finished_at=None,
        created_at=started_at,
    )

    with pytest.raises(HTTPException) as exception:
        update_session(
            session_id=1,
            payload=SessionUpdate(
                status="completed",
                finished_at=datetime(2026, 9, 9, 11, 59, tzinfo=UTC),
            ),
            repo=mock_repo,
        )

    assert exception.value.status_code == 422
    mock_repo.update.assert_not_called()


def test_list_sessions_by_camera() -> None:
    """Verifica que el endpoint GET liste las sesiones de una cámara."""
    mock_repo = MagicMock()
    now = datetime.now(UTC)
    mock_repo.get_all_by_camera.return_value = [
        SessionModel(
            id=1,
            camera_id=5,
            status="completed",
            started_at=now,
            finished_at=now,
            created_at=now,
        )
    ]
    response = list_sessions(camera_id=5, repo=mock_repo)
    assert len(response) == 1
    assert response[0].camera_id == 5

    mock_repo.get_all_by_camera.assert_called_once_with(camera_id=5)


def test_session_repository_does_not_create_for_an_unknown_camera() -> None:
    """La validación de cámara se realiza antes de persistir la sesión."""
    mock_db = MagicMock()
    mock_db.get.return_value = None
    repo = SessionRepository(session=mock_db)

    result = repo.create(camera_id=999, started_at=datetime.now(UTC))

    assert result is None
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
