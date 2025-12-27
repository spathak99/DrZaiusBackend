"""drop legacy storage_provider and storage_metadata columns from users

Revision ID: 20251208_0004
Revises: 20251208_0003
Create Date: 2025-12-08
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251208_0004"
down_revision = "20251208_0003"
branch_labels = None
depends_on = None


def _has_table(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def _has_column(bind, table: str, column: str) -> bool:
    insp = inspect(bind)
    try:
        cols = [c["name"] for c in insp.get_columns(table)]
    except Exception:
        return False
    return column in cols


def upgrade():
    bind = op.get_bind()
    if _has_table(bind, "users"):
        if _has_column(bind, "users", "storage_provider"):
            op.drop_column("users", "storage_provider")
        if _has_column(bind, "users", "storage_metadata"):
            op.drop_column("users", "storage_metadata")


def downgrade():
    bind = op.get_bind()
    if _has_table(bind, "users"):
        # Recreate columns as nullable to allow downgrade
        if not _has_column(bind, "users", "storage_provider"):
            op.add_column("users", sa.Column("storage_provider", sa.String(length=20), nullable=True))
        if not _has_column(bind, "users", "storage_metadata"):
            op.add_column("users", sa.Column("storage_metadata", sa.dialects.postgresql.JSONB, nullable=True))


