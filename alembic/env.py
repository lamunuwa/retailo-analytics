from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.src.core.db import Base, get_database_url
from app.src.models.analytics import DetectionEvent
from app.src.models.cameras import CameraModel
from app.src.models.sessions import SessionModel
from app.src.models.stores import StoreModel

# Alembic must import every model before it reads Base.metadata.
_models = (DetectionEvent, CameraModel, SessionModel, StoreModel)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_database_url())
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations using a short-lived Alembic connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
