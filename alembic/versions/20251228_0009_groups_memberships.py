"""create groups and group_memberships tables

Revision ID: 20251228_0009
Revises: 20251228_0008_rca
Create Date: 2025-12-29
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20251228_0009'
down_revision = '20251228_0008_rca'
branch_labels = None
depends_on = None


def _has_table(bind, table_name: str) -> bool:
	exists = bind.execute(
		text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :t)"),
		{"t": table_name},
	).scalar()
	return bool(exists)


def _has_index(bind, table_name: str, index_name: str) -> bool:
	q = text(
		"SELECT to_regclass(:idx) IS NOT NULL"
	)
	return bool(bind.execute(q, {"idx": index_name}).scalar())


def upgrade() -> None:
	bind = op.get_bind()

	# groups
	if not _has_table(bind, 'groups'):
		op.create_table(
			'groups',
			sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
			sa.Column('name', sa.String(length=255), nullable=False),
			sa.Column('description', sa.String(length=1024), nullable=True),
			sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
			sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
			sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
		)
		op.create_index('ix_groups_name', 'groups', ['name'])

	# group_memberships
	if not _has_table(bind, 'group_memberships'):
		op.create_table(
			'group_memberships',
			sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
			sa.Column('group_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
			sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
			sa.Column('role', sa.String(length=20), nullable=True),
			sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
			sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
			sa.UniqueConstraint('group_id', 'user_id', name='uq_group_membership_group_user'),
			sa.UniqueConstraint('user_id', name='uq_group_membership_user_unique'),
		)
		op.create_index('ix_group_memberships_group_id', 'group_memberships', ['group_id'])
		op.create_index('ix_group_memberships_user_id', 'group_memberships', ['user_id'])


def downgrade() -> None:
	# Drop in reverse order
	op.drop_index('ix_group_memberships_user_id', table_name='group_memberships')
	op.drop_index('ix_group_memberships_group_id', table_name='group_memberships')
	op.drop_table('group_memberships')
	op.drop_index('ix_groups_name', table_name='groups')
	op.drop_table('groups')


