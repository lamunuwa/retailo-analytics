"""Agrega la tabla de sesiones"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260909_0002"
down_revision: str | Sequence[str] | None = "20260909_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea la tabla de sesiones"""
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_camera_id", "sessions", ["camera_id"])
    op.create_index("ix_sessions_status", "sessions", ["status"])


def downgrade() -> None:
    """Elimina la tabla de sesiones"""
    op.drop_index("ix_sessions_status", table_name="sessions")
    op.drop_index("ix_sessions_camera_id", table_name="sessions")
    op.drop_table("sessions")
