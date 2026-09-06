from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./retailo.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Generador de sesión de base de datos para inyección de dependencias."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from collections.abc import Iterator

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

def get_db()-> Iterator[None]:
    yield None  # Placeholder para el TDD, luego pondremos el motor real
