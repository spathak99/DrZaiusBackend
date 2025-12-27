"""add user profile fields full_name, phone_number, age, country, avatar_uri

Revision ID: 20251208_0005
Revises: 20251208_0004
Create Date: 2025-12-08
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251208_0005"
down_revision = "20251208_0004"
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
        if not _has_column(bind, "users", "full_name"):
            op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))
        if not _has_column(bind, "users", "phone_number"):
            op.add_column("users", sa.Column("phone_number", sa.String(length=32), nullable=True))
        if not _has_column(bind, "users", "age"):
            op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))
        if not _has_column(bind, "users", "country"):
            op.add_column("users", sa.Column("country", sa.String(length=64), nullable=True))
        if not _has_column(bind, "users", "avatar_uri"):
            op.add_column("users", sa.Column("avatar_uri", sa.String(length=2048), nullable=True))


def downgrade():
    bind = op.get_bind()
    if _has_table(bind, "users"):
        for col in ["avatar_uri", "country", "age", "phone_number", "full_name"]:
            if _has_column(bind, "users", col):
                try:
                    op.drop_column("users", col)
                except Exception:
                    pass


