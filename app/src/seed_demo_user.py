import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.core.db import get_engine
from app.src.core.security import hash_password
from app.src.models.auth import UserModel


def seed_demo_user() -> None:
    """Crea la cuenta de demo cuando el entorno lo solicita."""
    if os.getenv("SEED_DEMO_USER", "false").casefold() != "true":
        return

    email = os.getenv("DEMO_USER_EMAIL", "dev@retailo.local").strip().casefold()
    password = os.getenv("DEMO_USER_PASSWORD", "retailo123")
    name = os.getenv("DEMO_USER_NAME", "Retailo Dev").strip()

    with Session(get_engine()) as session:
        existing_user = session.scalar(select(UserModel).where(UserModel.email == email))
        if existing_user is not None:
            return
        session.add(
            UserModel(
                name=name,
                email=email,
                password_hash=hash_password(password),
            )
        )
        session.commit()


if __name__ == "__main__":
    seed_demo_user()
