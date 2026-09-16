"""Agrega zonas resultados ventas y recomendaciones"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260915_0003"
down_revision: str | Sequence[str] | None = "20260909_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea las tablas restantes del MVP"""
    op.create_table(
        "zones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("zone_type", sa.String(length=30), nullable=False),
        sa.Column("points", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("camera_id", "name", name="uq_zones_camera_name"),
    )
    op.create_index("ix_zones_camera_id", "zones", ["camera_id"])

    op.create_table(
        "video_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("processed_frames", sa.Integer(), nullable=False),
        sa.Column("elapsed_seconds", sa.Float(), nullable=False),
        sa.Column("detected_people", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_video_results_session_id", "video_results", ["session_id"], unique=True)

    op.create_table(
        "zone_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("video_result_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("visits", sa.Integer(), nullable=False),
        sa.Column("dwell_seconds", sa.Float(), nullable=False),
        sa.Column("traffic_share", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["video_result_id"], ["video_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("video_result_id", "zone_id", name="uq_zone_metrics_result_zone"),
    )
    op.create_index("ix_zone_metrics_video_result_id", "zone_metrics", ["video_result_id"])
    op.create_index("ix_zone_metrics_zone_id", "zone_metrics", ["zone_id"])

    op.create_table(
        "sales_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("units_sold", sa.Integer(), nullable=False),
        sa.Column("revenue", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sales_records_store_id", "sales_records", ["store_id"])
    op.create_index("ix_sales_records_zone_id", "sales_records", ["zone_id"])
    op.create_index("ix_sales_records_recorded_at", "sales_records", ["recorded_at"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("zone_name", sa.String(length=100), nullable=False),
        sa.Column("insight_type", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("suggestion", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recommendations_store_id", "recommendations", ["store_id"])
    op.create_index("ix_recommendations_zone_id", "recommendations", ["zone_id"])
    op.create_index("ix_recommendations_status", "recommendations", ["status"])


def downgrade() -> None:
    """Elimina las tablas restantes del MVP"""
    op.drop_index("ix_recommendations_status", table_name="recommendations")
    op.drop_index("ix_recommendations_zone_id", table_name="recommendations")
    op.drop_index("ix_recommendations_store_id", table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_index("ix_sales_records_recorded_at", table_name="sales_records")
    op.drop_index("ix_sales_records_zone_id", table_name="sales_records")
    op.drop_index("ix_sales_records_store_id", table_name="sales_records")
    op.drop_table("sales_records")
    op.drop_index("ix_zone_metrics_zone_id", table_name="zone_metrics")
    op.drop_index("ix_zone_metrics_video_result_id", table_name="zone_metrics")
    op.drop_table("zone_metrics")
    op.drop_index("ix_video_results_session_id", table_name="video_results")
    op.drop_table("video_results")
    op.drop_index("ix_zones_camera_id", table_name="zones")
    op.drop_table("zones")
