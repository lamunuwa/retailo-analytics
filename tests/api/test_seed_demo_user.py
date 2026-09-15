from unittest.mock import MagicMock, patch

import pytest

from app.src.core.security import verify_password
from app.src.models.auth import UserModel
from app.src.seed_demo_user import seed_demo_user


def test_seed_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """No crea una cuenta sin la bandera de demo."""
    monkeypatch.delenv("SEED_DEMO_USER", raising=False)

    with patch("app.src.seed_demo_user.get_engine") as get_engine:
        seed_demo_user()

    get_engine.assert_not_called()


def test_seed_creates_the_configured_demo_user(monkeypatch: pytest.MonkeyPatch) -> None:
    """Crea la cuenta configurada cuando no existe."""
    monkeypatch.setenv("SEED_DEMO_USER", "true")
    monkeypatch.setenv("DEMO_USER_NAME", "Usuario Demo")
    monkeypatch.setenv("DEMO_USER_EMAIL", "DEMO@RETAILO.LOCAL")
    monkeypatch.setenv("DEMO_USER_PASSWORD", "secreto123")
    session = MagicMock()
    session.scalar.return_value = None

    with (
        patch("app.src.seed_demo_user.get_engine", return_value=MagicMock()),
        patch("app.src.seed_demo_user.Session") as session_class,
    ):
        session_class.return_value.__enter__.return_value = session
        seed_demo_user()

    user = session.add.call_args.args[0]
    assert isinstance(user, UserModel)
    assert user.name == "Usuario Demo"
    assert user.email == "demo@retailo.local"
    assert verify_password("secreto123", user.password_hash)
    session.commit.assert_called_once()


def test_seed_keeps_an_existing_account(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita duplicar la cuenta de demo."""
    monkeypatch.setenv("SEED_DEMO_USER", "true")
    session = MagicMock()
    session.scalar.return_value = UserModel(
        id=1,
        name="Retailo Dev",
        email="dev@retailo.local",
        password_hash="hash",
    )

    with (
        patch("app.src.seed_demo_user.get_engine", return_value=MagicMock()),
        patch("app.src.seed_demo_user.Session") as session_class,
    ):
        session_class.return_value.__enter__.return_value = session
        seed_demo_user()

    session.add.assert_not_called()
    session.commit.assert_not_called()
