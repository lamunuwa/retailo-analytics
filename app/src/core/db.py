from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

def get_db():
    yield None  # Placeholder para el TDD, luego pondremos el motor real