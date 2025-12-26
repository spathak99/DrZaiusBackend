"""drop legacy local chat/files tables

Revision ID: 20251208_0002
Revises: 20251208_0001
Create Date: 2025-12-08
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251208_0002"
down_revision = "20251208_0001"
branch_labels = None
depends_on = None


def _has_table(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade():
    bind = op.get_bind()
    # Drop in dependency-safe order and use CASCADE to avoid FK issues
    drop_order = ["messages", "chat_participants", "file_access", "files", "chats"]
    for tbl in drop_order:
        if _has_table(bind, tbl):
            op.execute(f'DROP TABLE IF EXISTS "{tbl}" CASCADE')


def downgrade():
    # No-op: re-creating legacy tables intentionally omitted
    pass


