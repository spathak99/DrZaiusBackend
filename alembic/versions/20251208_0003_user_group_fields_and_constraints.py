"""add user fields for project/buckets/account and group constraint

Revision ID: 20251208_0003
Revises: 20251208_0002
Create Date: 2025-12-08
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251208_0003"
down_revision = "20251208_0002"
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
        if not _has_column(bind, "users", "account_type"):
            op.add_column("users", sa.Column("account_type", sa.String(length=20), nullable=True))
        if not _has_column(bind, "users", "group_id"):
            op.add_column("users", sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=True))
            op.create_foreign_key(
                "fk_users_group_id_groups",
                "users",
                "groups",
                ["group_id"],
                ["id"],
                ondelete="SET NULL",
            )
        if not _has_column(bind, "users", "gcp_project_id"):
            op.add_column("users", sa.Column("gcp_project_id", sa.String(length=128), nullable=True))
        if not _has_column(bind, "users", "temp_bucket"):
            op.add_column("users", sa.Column("temp_bucket", sa.String(length=1024), nullable=True))
        if not _has_column(bind, "users", "payment_info"):
            op.add_column("users", sa.Column("payment_info", postgresql.JSONB, nullable=True))

    if _has_table(bind, "groups"):
        if not _has_column(bind, "groups", "payment_info"):
            op.add_column("groups", sa.Column("payment_info", postgresql.JSONB, nullable=True))

    if _has_table(bind, "group_memberships"):
        # unique per user
        op.create_unique_constraint(
            "uq_group_membership_user_unique", "group_memberships", ["user_id"]
        )


def downgrade():
    bind = op.get_bind()
    if _has_table(bind, "group_memberships"):
        try:
            op.drop_constraint("uq_group_membership_user_unique", "group_memberships", type_="unique")
        except Exception:
            pass
    if _has_table(bind, "groups"):
        if _has_column(bind, "groups", "payment_info"):
            op.drop_column("groups", "payment_info")
    if _has_table(bind, "users"):
        for col in ["payment_info", "temp_bucket", "gcp_project_id", "group_id", "account_type"]:
            if _has_column(bind, "users", col):
                try:
                    if col == "group_id":
                        op.drop_constraint("fk_users_group_id_groups", "users", type_="foreignkey")
                    op.drop_column("users", col)
                except Exception:
                    pass


