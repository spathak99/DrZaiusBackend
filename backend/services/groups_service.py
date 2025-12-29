from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import Errors, Keys, Fields, GroupRoles
from backend.db.models import Group, GroupMembership, User
from backend.repositories.groups_repo import GroupsRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository


class GroupsService:
	def __init__(self) -> None:
		self.groups_repo = GroupsRepository()
		self.members_repo = GroupMembershipsRepository()

	def create(self, db: Session, *, name: str, description: Optional[str], created_by: str) -> Dict[str, Any]:
		group = self.groups_repo.create(db, name=name, description=description, created_by=created_by)
		return {
			Fields.ID: str(group.id),
			Fields.NAME: group.name,
			Fields.DESCRIPTION: group.description,
			Fields.CREATED_BY: str(group.created_by),
			Fields.CREATED_AT: group.created_at,
		}

	def list_mine(self, db: Session, *, user_id: str) -> List[Dict[str, Any]]:
		rows = self.groups_repo.list_mine(db, user_id=user_id)
		return [{Fields.ID: str(g.id), Fields.NAME: g.name, Fields.DESCRIPTION: g.description} for g in rows]

	def get(self, db: Session, *, group_id: str, user_id: str) -> Dict[str, Any]:
		group = self.groups_repo.get(db, group_id=group_id)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		mine = self.members_repo.get(db, group_id=group_id, user_id=user_id)
		if mine is None:
			raise ValueError(Errors.FORBIDDEN)
		return {Fields.ID: str(group.id), Fields.NAME: group.name, Fields.DESCRIPTION: group.description}

	def update(self, db: Session, *, group_id: str, user_id: str, name: str, description: Optional[str]) -> Dict[str, Any]:
		# Only admins can update group
		role = self.members_repo.get(db, group_id=group_id, user_id=user_id)
		if role is None or role.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)
		group = self.groups_repo.update_name(db, group_id=group_id, name=name, description=description)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		return {
			Fields.ID: str(group.id),
			Fields.NAME: group.name,
			Fields.DESCRIPTION: group.description,
			Fields.CREATED_BY: str(group.created_by),
			Fields.CREATED_AT: group.created_at,
		}

	def delete(self, db: Session, *, group_id: str, user_id: str) -> None:
		# Only admins can delete; must be member
		mine = self.members_repo.get(db, group_id=group_id, user_id=user_id)
		if mine is None or mine.role != "admin":
			raise ValueError(Errors.FORBIDDEN)
		self.groups_repo.delete(db, group_id=group_id)
		return


class MembershipsService:
	def __init__(self) -> None:
		self.groups_repo = GroupsRepository()
		self.repo = GroupMembershipsRepository()

	def _ensure_admin(self, db: Session, *, group_id: str, actor_id: str) -> None:
		m = self.repo.get(db, group_id=group_id, user_id=actor_id)
		if m is None or m.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)

	def list_by_group(self, db: Session, *, group_id: str, actor_id: str) -> List[Dict[str, Any]]:
		# Any member can list
		m = self.repo.get(db, group_id=group_id, user_id=actor_id)
		if m is None:
			raise ValueError(Errors.FORBIDDEN)
		rows = self.repo.list_by_group(db, group_id=group_id)
		return [{Fields.ID: str(r.id), Keys.USER_ID: str(r.user_id), Fields.ROLE: r.role} for r in rows]

	def add(self, db: Session, *, group_id: str, actor_id: str, user_id: str, role: str = "member") -> Dict[str, Any]:
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		row = self.repo.add(db, group_id=group_id, user_id=user_id, role=role)
		return {Fields.ID: str(row.id), Keys.USER_ID: str(row.user_id), Fields.ROLE: row.role}

	def change_role(self, db: Session, *, group_id: str, actor_id: str, user_id: str, role: str) -> Dict[str, Any]:
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		row = self.repo.change_role(db, group_id=group_id, user_id=user_id, role=role)
		if row is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		# Last-admin guard: ensure at least one admin remains
		if self.repo.count_admins(db, group_id=group_id) < 1:
			# revert
			self.repo.change_role(db, group_id=group_id, user_id=user_id, role=GroupRoles.ADMIN)
			raise ValueError(Errors.FORBIDDEN)
		return {Fields.ID: str(row.id), Keys.USER_ID: str(row.user_id), Fields.ROLE: row.role}

	def remove(self, db: Session, *, group_id: str, actor_id: str, user_id: str) -> None:
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		# If removing an admin, ensure at least one remains
		m = self.repo.get(db, group_id=group_id, user_id=user_id)
		if m is None:
			return
		self.repo.remove(db, group_id=group_id, user_id=user_id)
		if m.role == GroupRoles.ADMIN and self.repo.count_admins(db, group_id=group_id) < 1:
			# undo by re-adding as admin
			self.repo.add(db, group_id=group_id, user_id=user_id, role=GroupRoles.ADMIN)
			raise ValueError(Errors.FORBIDDEN)
		return

	def leave(self, db: Session, *, group_id: str, user_id: str) -> None:
		m = self.repo.get(db, group_id=group_id, user_id=user_id)
		if m is None:
			return
		self.repo.remove(db, group_id=group_id, user_id=user_id)
		# Last-admin guard if leaver was admin
		if m.role == GroupRoles.ADMIN and self.repo.count_admins(db, group_id=group_id) < 1:
			# re-add as admin (can't leave if last admin)
			self.repo.add(db, group_id=group_id, user_id=user_id, role=GroupRoles.ADMIN)
			raise ValueError(Errors.FORBIDDEN)
		return


