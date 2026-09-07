from collections.abc import Iterator

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[None]:
    yield None  # Placeholder para el TDD, luego pondremos el motor real
