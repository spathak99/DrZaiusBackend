"""group member invites

Revision ID: 20251231_0011
Revises: 20251228_0010
Create Date: 2025-12-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251231_0011"
down_revision = "20251228_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"group_member_invites",
		sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
		sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
		sa.Column("invited_email", sa.String(length=255), nullable=False),
		sa.Column("invited_full_name", sa.String(length=255), nullable=True),
		sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
		sa.Column("invited_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
		sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
		sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
		sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
	)
	# index on invited_email for quick lookups
	op.create_index("ix_group_member_invites_invited_email", "group_member_invites", ["invited_email"])
	# partial unique for pending invites per (group_id, invited_email)
	op.create_index(
		"uq_group_member_invites_pending",
		"group_member_invites",
		["group_id", "invited_email"],
		unique=True,
		postgresql_where=sa.text("status = 'pending'"),
	)


def downgrade() -> None:
	op.drop_index("uq_group_member_invites_pending", table_name="group_member_invites")
	op.drop_index("ix_group_member_invites_invited_email", table_name="group_member_invites")
	op.drop_table("group_member_invites")


