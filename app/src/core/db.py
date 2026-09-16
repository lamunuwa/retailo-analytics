import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurada")

    # Render entrega una URL ``postgresql://``. SQLAlchemy interpreta ese
    # esquema como psycopg2 por defecto, pero la aplicación instala Psycopg 3.
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def get_engine() -> Engine:
    """Crea la conexión sólo cuando una petición necesita la base de datos."""
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """Abre una sesión por petición y la cierra al terminar."""
    db = SessionLocal(bind=get_engine())
    try:
        yield db
    finally:
        db.close()
