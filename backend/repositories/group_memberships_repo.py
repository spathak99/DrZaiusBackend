from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.db.models import GroupMembership, Group, User


class GroupMembershipsRepository:
	def get(self, db: Session, *, group_id: str, user_id: str) -> Optional[GroupMembership]:
		return db.scalar(
			select(GroupMembership).where(
				GroupMembership.group_id == group_id,
				GroupMembership.user_id == user_id,
			)
		)

	def list_by_group(self, db: Session, *, group_id: str) -> List[GroupMembership]:
		return db.scalars(select(GroupMembership).where(GroupMembership.group_id == group_id)).all()

	def list_mine(self, db: Session, *, user_id: str) -> List[GroupMembership]:
		return db.scalars(select(GroupMembership).where(GroupMembership.user_id == user_id)).all()

	def count_admins(self, db: Session, *, group_id: str) -> int:
		return int(
			db.scalar(
				select(func.count()).where(
					GroupMembership.group_id == group_id,
					GroupMembership.role == "admin",
				)
			)
			or 0
		)

	def add(self, db: Session, *, group_id: str, user_id: str, role: str) -> GroupMembership:
		row = GroupMembership(group_id=group_id, user_id=user_id, role=role)
		db.add(row)
		db.commit()
		db.refresh(row)
		return row

	def remove(self, db: Session, *, group_id: str, user_id: str) -> None:
		row = self.get(db, group_id=group_id, user_id=user_id)
		if row is None:
			return
		db.delete(row)
		db.commit()
		return

	def change_role(self, db: Session, *, group_id: str, user_id: str, role: str) -> Optional[GroupMembership]:
		row = self.get(db, group_id=group_id, user_id=user_id)
		if row is None:
			return None
		row.role = role
		db.commit()
		db.refresh(row)
		return row


