from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.db.models import Group, GroupMembership, User
from backend.core.constants import GroupRoles


class GroupsRepository:
	def create(self, db: Session, *, name: str, description: Optional[str], created_by: str) -> Group:
		group = Group(name=name, description=description, created_by=created_by)
		db.add(group)
		db.commit()
		db.refresh(group)
		# Creator becomes admin member
		m = GroupMembership(group_id=group.id, user_id=created_by, role=GroupRoles.ADMIN)
		db.add(m)
		db.commit()
		return group

	def list_mine(self, db: Session, *, user_id: str) -> List[Group]:
		rows = db.scalars(
			select(Group).join(GroupMembership, Group.id == GroupMembership.group_id).where(GroupMembership.user_id == user_id)
		).all()
		return rows

	def get(self, db: Session, *, group_id: str) -> Optional[Group]:
		return db.scalar(select(Group).where(Group.id == group_id))

	def update_name(self, db: Session, *, group_id: str, name: str, description: Optional[str] = None) -> Optional[Group]:
		group = self.get(db, group_id=group_id)
		if group is None:
			return None
		group.name = name
		if description is not None:
			group.description = description
		db.commit()
		db.refresh(group)
		return group

	def delete(self, db: Session, *, group_id: str) -> None:
		group = self.get(db, group_id=group_id)
		if group is None:
			return
		db.delete(group)
		db.commit()
		return


