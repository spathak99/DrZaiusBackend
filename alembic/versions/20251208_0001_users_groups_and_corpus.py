"""users: corpus/chat_history, groups and memberships

Revision ID: 20251208_0001
Revises: None
Create Date: 2025-12-08
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = "20251208_0001"
down_revision = None
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

    # users.corpus_uri: rename storage_root_uri if present, else add new
    if _has_table(bind, "users"):
        if _has_column(bind, "users", "corpus_uri"):
            pass
        elif _has_column(bind, "users", "storage_root_uri"):
            op.alter_column("users", "storage_root_uri", new_column_name="corpus_uri")
        else:
            op.add_column("users", sa.Column("corpus_uri", sa.String(length=2048), nullable=True))
            # backfill empty string to avoid nulls, then make non-nullable
            op.execute(text("UPDATE users SET corpus_uri = '' WHERE corpus_uri IS NULL"))
            op.alter_column("users", "corpus_uri", nullable=False)

        # users.chat_history_uri nullable
        if not _has_column(bind, "users", "chat_history_uri"):
            op.add_column("users", sa.Column("chat_history_uri", sa.String(length=2048), nullable=True))
    else:
        # Fresh DB: create a minimal users table that satisfies current and future FKs
        op.create_table(
            "users",
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("username", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("corpus_uri", sa.String(length=2048), nullable=False, server_default=""),
            sa.Column("chat_history_uri", sa.String(length=2048), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        )
        op.create_index("ix_users_username", "users", ["username"], unique=True)
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    # groups table
    if not _has_table(bind, "groups"):
        op.create_table(
            "groups",
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False, index=True),
            sa.Column("description", sa.String(length=1024), nullable=True),
            sa.Column("created_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        )
        op.create_index("idx_groups_name", "groups", ["name"])

    # group_memberships table
    if not _has_table(bind, "group_memberships"):
        op.create_table(
            "group_memberships",
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("group_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        )
        op.create_index("idx_group_memberships_group", "group_memberships", ["group_id"])
        op.create_index("idx_group_memberships_user", "group_memberships", ["user_id"])
        op.create_unique_constraint(
            "uq_group_membership_group_user", "group_memberships", ["group_id", "user_id"]
        )


def downgrade():
    bind = op.get_bind()
    if _has_table(bind, "group_memberships"):
        try:
            op.drop_constraint("uq_group_membership_group_user", "group_memberships", type_="unique")
        except Exception:
            pass
        try:
            op.drop_index("idx_group_memberships_group", table_name="group_memberships")
        except Exception:
            pass
        try:
            op.drop_index("idx_group_memberships_user", table_name="group_memberships")
        except Exception:
            pass
        op.drop_table("group_memberships")

    if _has_table(bind, "groups"):
        try:
            op.drop_index("idx_groups_name", table_name="groups")
        except Exception:
            pass
        op.drop_table("groups")

    if _has_table(bind, "users"):
        if _has_column(bind, "users", "chat_history_uri"):
            op.drop_column("users", "chat_history_uri")
        # Attempt to rename corpus_uri back, else drop it
        if _has_column(bind, "users", "corpus_uri"):
            op.alter_column("users", "corpus_uri", new_column_name="storage_root_uri")


