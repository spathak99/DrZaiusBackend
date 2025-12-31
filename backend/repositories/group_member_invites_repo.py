from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.db.models import GroupMemberInvite
from backend.schemas.common import InvitationStatus


class GroupMemberInvitesRepository:
	def create(self, db: Session, *, group_id: str, invited_email: str, invited_full_name: Optional[str], invited_by: str, expires_at=None) -> GroupMemberInvite:
		row = GroupMemberInvite(
			group_id=group_id,
			invited_email=invited_email,
			invited_full_name=invited_full_name,
			status="pending",
			invited_by=invited_by,
			expires_at=expires_at,
		)
		db.add(row)
		db.commit()
		db.refresh(row)
		return row

	def get(self, db: Session, *, invite_id: str) -> Optional[GroupMemberInvite]:
		return db.scalar(select(GroupMemberInvite).where(GroupMemberInvite.id == invite_id))

	def get_pending_by_email(self, db: Session, *, group_id: str, email: str) -> Optional[GroupMemberInvite]:
		return db.scalar(
			select(GroupMemberInvite).where(
				GroupMemberInvite.group_id == group_id,
				GroupMemberInvite.invited_email == email,
				GroupMemberInvite.status == InvitationStatus.pending.value,
			)
		)

	def list_pending_paginated(self, db: Session, *, group_id: str, limit: int, offset: int) -> List[GroupMemberInvite]:
		return db.scalars(
			select(GroupMemberInvite)
			.where(GroupMemberInvite.group_id == group_id, GroupMemberInvite.status == InvitationStatus.pending.value)
			.order_by(GroupMemberInvite.created_at)
			.limit(limit)
			.offset(offset)
		).all()

	def count_pending(self, db: Session, *, group_id: str) -> int:
		return int(
			db.scalar(
				select(func.count()).select_from(GroupMemberInvite).where(
					GroupMemberInvite.group_id == group_id, GroupMemberInvite.status == InvitationStatus.pending.value
				)
			)
			or 0
		)

	def set_status(self, db: Session, *, invite: GroupMemberInvite, status: str) -> None:
		invite.status = status
		db.commit()
		db.refresh(invite)


