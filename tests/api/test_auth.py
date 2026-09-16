from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.src.core.db import Base, get_db
from app.src.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Crea un cliente con una base aislada."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_db() -> Iterator[Session]:
        """Entrega una sesion aislada para la prueba."""
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def register_user(client: TestClient) -> dict[str, object]:
    """Registra el usuario base de una prueba."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Retailo Dev",
            "email": "DEV@RETAILO.LOCAL",
            "password": "retailo123",
        },
    )
    assert response.status_code == 201
    return cast(dict[str, object], response.json())


def test_register_normalizes_email_and_returns_session(client: TestClient) -> None:
    """Valida el registro y la normalizacion del correo."""
    body = register_user(client)

    assert body["token_type"] == "bearer"
    assert len(str(body["access_token"])) > 30
    assert body["user"]["name"] == "Retailo Dev"  # type: ignore[index]
    assert body["user"]["email"] == "dev@retailo.local"  # type: ignore[index]


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    """Rechaza un correo ya registrado."""
    register_user(client)

    response = client.post(
        "/auth/register",
        json={"name": "Otro", "email": "dev@retailo.local", "password": "abcdef"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "El correo ya esta registrado"


def test_register_rejects_short_password(client: TestClient) -> None:
    """Rechaza una contrasena menor a seis caracteres."""
    response = client.post(
        "/auth/register",
        json={"name": "Retailo Dev", "email": "dev@retailo.local", "password": "12345"},
    )

    assert response.status_code == 422


def test_login_and_current_user(client: TestClient) -> None:
    """Valida el inicio y la consulta de sesion."""
    register_user(client)
    login_response = client.post(
        "/auth/login",
        json={"email": "DEV@RETAILO.LOCAL", "password": "retailo123"},
    )
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert login_response.status_code == 200
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "dev@retailo.local"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    """Rechaza credenciales incorrectas."""
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "dev@retailo.local", "password": "incorrecta"},
    )

    assert response.status_code == 401


def test_password_change_replaces_credentials(client: TestClient) -> None:
    """Valida el cambio de contrasena."""
    registered = register_user(client)
    token = registered["access_token"]

    change_response = client.patch(
        "/auth/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "retailo123", "new_password": "nueva123"},
    )
    old_login = client.post(
        "/auth/login",
        json={"email": "dev@retailo.local", "password": "retailo123"},
    )
    new_login = client.post(
        "/auth/login",
        json={"email": "dev@retailo.local", "password": "nueva123"},
    )

    assert change_response.status_code == 204
    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_password_change_rejects_wrong_current_password(client: TestClient) -> None:
    """Rechaza una contrasena actual incorrecta."""
    registered = register_user(client)

    response = client.patch(
        "/auth/password",
        headers={"Authorization": f"Bearer {registered['access_token']}"},
        json={"current_password": "incorrecta", "new_password": "nueva123"},
    )

    assert response.status_code == 400


def test_logout_invalidates_session(client: TestClient) -> None:
    """Valida que cerrar sesion invalide el token."""
    registered = register_user(client)
    headers = {"Authorization": f"Bearer {registered['access_token']}"}

    logout_response = client.post("/auth/logout", headers=headers)
    me_response = client.get("/auth/me", headers=headers)

    assert logout_response.status_code == 204
    assert me_response.status_code == 401


def test_current_user_requires_token(client: TestClient) -> None:
    """Rechaza una consulta sin token."""
    response = client.get("/auth/me")

    assert response.status_code == 401
