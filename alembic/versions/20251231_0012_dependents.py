"""dependents

Revision ID: 20251231_0012
Revises: 20251231_0011
Create Date: 2025-12-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251231_0012"
down_revision = "20251231_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"dependents",
		sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
		sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
		sa.Column("guardian_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
		sa.Column("full_name", sa.String(length=255), nullable=True),
		sa.Column("dob", sa.Date(), nullable=True),
		sa.Column("email", sa.String(length=255), nullable=True),
		sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
		sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
		sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
	)
	op.create_index("ix_dependents_group_id", "dependents", ["group_id"])
	op.create_index("ix_dependents_guardian_id", "dependents", ["guardian_user_id"])


def downgrade() -> None:
	op.drop_index("ix_dependents_guardian_id", table_name="dependents")
	op.drop_index("ix_dependents_group_id", table_name="dependents")
	op.drop_table("dependents")


