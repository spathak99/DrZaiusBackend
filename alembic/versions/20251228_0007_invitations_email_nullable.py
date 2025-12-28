from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
# Keep <= 32 chars for version_num column
revision = "20251228_0007_invite_email"
down_revision = "20251228_0006_invitation_sent_by"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = insp.get_table_names()
    if "invitations" not in tables:
        return

    cols = [c["name"] for c in insp.get_columns("invitations")]

    if "invited_email" not in cols:
        op.add_column("invitations", sa.Column("invited_email", sa.String(length=255), nullable=True))
    if "invited_full_name" not in cols:
        op.add_column("invitations", sa.Column("invited_full_name", sa.String(length=255), nullable=True))

    # Relax NOT NULL on caregiver_id / recipient_id if present
    # Use SQL to avoid cross-dialect nuances; target is Postgres
    try:
        op.execute(text("ALTER TABLE invitations ALTER COLUMN caregiver_id DROP NOT NULL"))
    except Exception:
        pass
    try:
        op.execute(text("ALTER TABLE invitations ALTER COLUMN recipient_id DROP NOT NULL"))
    except Exception:
        pass


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = insp.get_table_names()
    if "invitations" not in tables:
        return
    cols = [c["name"] for c in insp.get_columns("invitations")]
    if "invited_full_name" in cols:
        op.drop_column("invitations", "invited_full_name")
    if "invited_email" in cols:
        op.drop_column("invitations", "invited_email")
    # Do not re-impose NOT NULL automatically, as data may exist; manual rollback if needed


