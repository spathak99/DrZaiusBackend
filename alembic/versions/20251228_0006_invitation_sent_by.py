from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251228_0006_invitation_sent_by'
down_revision = '20251208_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    def _has_table(connection, table_name: str) -> bool:
        insp = inspect(connection)
        return table_name in insp.get_table_names()

    def _has_column(connection, table: str, column: str) -> bool:
        insp = inspect(connection)
        try:
            cols = [c["name"] for c in insp.get_columns(table)]
        except Exception:
            return False
        return column in cols

    # If invitations table is missing (fresh DB), create it including sent_by.
    if not _has_table(bind, "invitations"):
        op.create_table(
            "invitations",
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("caregiver_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("recipient_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("sent_by", sa.String(length=20), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        )
    else:
        # Table exists; add the new column if missing
        if not _has_column(bind, "invitations", "sent_by"):
            op.add_column("invitations", sa.Column("sent_by", sa.String(length=20), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = insp.get_table_names()
    if "invitations" in tables:
        cols = [c["name"] for c in insp.get_columns("invitations")]
        if "sent_by" in cols:
            op.drop_column("invitations", "sent_by")


