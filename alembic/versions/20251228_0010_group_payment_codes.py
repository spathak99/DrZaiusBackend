"""create group_payment_codes

Revision ID: 20251228_0010
Revises: 20251228_0009
Create Date: 2025-12-29
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20251228_0010'
down_revision = '20251228_0009'
branch_labels = None
depends_on = None


def _has_table(bind, table: str) -> bool:
	return bool(bind.execute(text("SELECT to_regclass(:t) IS NOT NULL"), {"t": table}).scalar())


def upgrade() -> None:
	bind = op.get_bind()
	if not _has_table(bind, 'group_payment_codes'):
		op.create_table(
			'group_payment_codes',
			sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
			sa.Column('group_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
			sa.Column('code', sa.String(length=64), nullable=False, unique=True),
			sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
			sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
			sa.Column('redeemed_by', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
			sa.Column('redeemed_at', sa.DateTime(timezone=True), nullable=True),
			sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
			sa.Column('meta', sa.dialects.postgresql.JSONB, nullable=True),
			sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
			sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
		)
		op.create_index('ix_group_payment_codes_code', 'group_payment_codes', ['code'])
		op.create_index('ix_group_payment_codes_group_id', 'group_payment_codes', ['group_id'])


def downgrade() -> None:
	op.drop_index('ix_group_payment_codes_group_id', table_name='group_payment_codes')
	op.drop_index('ix_group_payment_codes_code', table_name='group_payment_codes')
	op.drop_table('group_payment_codes')


