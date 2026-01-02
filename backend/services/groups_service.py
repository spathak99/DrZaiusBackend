"""Groups services: manage groups and memberships."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import Errors, Keys, Fields, GroupRoles, LogEvents
from backend.db.models import Group, GroupMembership, User
from backend.repositories.groups_repo import GroupsRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository


class GroupsService:
	"""Service to create, list, get, update and delete groups."""
	def __init__(self, *, groups_repo: GroupsRepository | None = None, members_repo: GroupMembershipsRepository | None = None) -> None:
		self.groups_repo = groups_repo or GroupsRepository()
		self.members_repo = members_repo or GroupMembershipsRepository()
		self.logger = logging.getLogger(__name__)

	def create(self, db: Session, *, name: str, description: Optional[str], created_by: str) -> Dict[str, Any]:
		"""Create a group and add the creator as admin."""
		group = self.groups_repo.create(db, name=name, description=description, created_by=created_by)
		# Ensure creator is a member and an admin (idempotent)
		self.members_repo.add(db, group_id=str(group.id), user_id=created_by, role=GroupRoles.ADMIN)
		self.logger.info(LogEvents.GROUP_CREATED, extra={Keys.GROUP_ID: str(group.id), Keys.ACTOR_ID: created_by})
		return {
			Fields.ID: str(group.id),
			Fields.NAME: group.name,
			Fields.DESCRIPTION: group.description,
			Fields.CREATED_BY: str(group.created_by),
			Fields.CREATED_AT: group.created_at,
		}

	def list_mine(self, db: Session, *, user_id: str) -> List[Dict[str, Any]]:
		"""List groups the user belongs to."""
		rows = self.groups_repo.list_mine(db, user_id=user_id)
		return [{Fields.ID: str(g.id), Fields.NAME: g.name, Fields.DESCRIPTION: g.description} for g in rows]

	def get(self, db: Session, *, group_id: str, user_id: str) -> Dict[str, Any]:
		"""Get a group's details if the user is a member."""
		group = self.groups_repo.get(db, group_id=group_id)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		mine = self.members_repo.get(db, group_id=group_id, user_id=user_id)
		if mine is None:
			raise ValueError(Errors.FORBIDDEN)
		return {
			Fields.ID: str(group.id),
			Fields.NAME: group.name,
			Fields.DESCRIPTION: group.description,
			Fields.CREATED_BY: str(group.created_by) if getattr(group, "created_by", None) is not None else "",
			Fields.CREATED_AT: getattr(group, "created_at", None),
		}

	def update(self, db: Session, *, group_id: str, user_id: str, name: str, description: Optional[str]) -> Dict[str, Any]:
		"""Update group name/description (admins only)."""
		# Only admins can update group
		role = self.members_repo.get(db, group_id=group_id, user_id=user_id)
		if role is None or role.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)
		group = self.groups_repo.update_name(db, group_id=group_id, name=name, description=description)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		self.logger.info(LogEvents.GROUP_UPDATED, extra={Keys.GROUP_ID: str(group.id), Keys.ACTOR_ID: user_id})
		return {
			Fields.ID: str(group.id),
			Fields.NAME: group.name,
			Fields.DESCRIPTION: group.description,
			Fields.CREATED_BY: str(group.created_by),
			Fields.CREATED_AT: group.created_at,
		}

	def delete(self, db: Session, *, group_id: str, user_id: str) -> None:
		"""Delete a group (admins only)."""
		# Only admins can delete; must be member
		mine = self.members_repo.get(db, group_id=group_id, user_id=user_id)
		if mine is None or mine.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)
		self.groups_repo.delete(db, group_id=group_id)
		self.logger.info(LogEvents.GROUP_DELETED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: user_id})
		return


class MembershipsService:
	"""Service for managing group memberships and roles."""
	def __init__(self, *, groups_repo: GroupsRepository | None = None, memberships_repo: GroupMembershipsRepository | None = None) -> None:
		self.groups_repo = groups_repo or GroupsRepository()
		self.repo = memberships_repo or GroupMembershipsRepository()
		self.logger = logging.getLogger(__name__)

	def _ensure_admin(self, db: Session, *, group_id: str, actor_id: str) -> None:
		"""Validate the actor is an admin of the group."""
		m = self.repo.get(db, group_id=group_id, user_id=actor_id)
		if m is None or m.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)

	def list_by_group(self, db: Session, *, group_id: str, actor_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
		"""List members of a group with roles."""
		# Any member can list
		m = self.repo.get(db, group_id=group_id, user_id=actor_id)
		if m is None:
			raise ValueError(Errors.FORBIDDEN)
		total = self.repo.count_by_group(db, group_id=group_id)
		rows = self.repo.list_by_group_paginated(db, group_id=group_id, limit=limit, offset=offset)
		items = [{Fields.ID: str(r.id), Keys.USER_ID: str(r.user_id), Fields.ROLE: r.role} for r in rows]
		return {Keys.ITEMS: items, Keys.TOTAL: total}

	def add(self, db: Session, *, group_id: str, actor_id: str, user_id: str, role: str = GroupRoles.MEMBER) -> Dict[str, Any]:
		"""Add a user to a group (admin only)."""
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		row = self.repo.add(db, group_id=group_id, user_id=user_id, role=role)
		self.logger.info(LogEvents.GROUP_MEMBER_ADDED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.TARGET_USER_ID: user_id, Fields.ROLE: role})
		return {Fields.ID: str(row.id), Keys.USER_ID: str(row.user_id), Fields.ROLE: row.role}

	def change_role(self, db: Session, *, group_id: str, actor_id: str, user_id: str, role: str) -> Dict[str, Any]:
		"""Change a member's role (admin-only with last-admin safeguards)."""
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		# Do not allow demoting the creator from admin
		group = self.groups_repo.get(db, group_id=group_id)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		if str(group.created_by) == str(user_id) and role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)
		row = self.repo.change_role(db, group_id=group_id, user_id=user_id, role=role)
		if row is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		# Last-admin guard: ensure at least one admin remains
		if self.repo.count_admins(db, group_id=group_id) < 1:
			# revert
			self.repo.change_role(db, group_id=group_id, user_id=user_id, role=GroupRoles.ADMIN)
			raise ValueError(Errors.FORBIDDEN)
		self.logger.info(LogEvents.GROUP_MEMBER_ROLE_CHANGED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.TARGET_USER_ID: user_id, Fields.ROLE: role})
		return {Fields.ID: str(row.id), Keys.USER_ID: str(row.user_id), Fields.ROLE: row.role}

	def remove(self, db: Session, *, group_id: str, actor_id: str, user_id: str) -> None:
		"""Remove a user from a group (admin only, creator cannot be removed)."""
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		# Do not allow removing the creator from the group
		group = self.groups_repo.get(db, group_id=group_id)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		if str(group.created_by) == str(user_id):
			raise ValueError(Errors.FORBIDDEN)
		# If removing an admin, ensure at least one remains
		m = self.repo.get(db, group_id=group_id, user_id=user_id)
		if m is None:
			return
		self.repo.remove(db, group_id=group_id, user_id=user_id)
		if m.role == GroupRoles.ADMIN and self.repo.count_admins(db, group_id=group_id) < 1:
			# undo by re-adding as admin
			self.repo.add(db, group_id=group_id, user_id=user_id, role=GroupRoles.ADMIN)
			raise ValueError(Errors.FORBIDDEN)
		self.logger.info(LogEvents.GROUP_MEMBER_REMOVED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.TARGET_USER_ID: user_id, Fields.ROLE: m.role})
		return

	def leave(self, db: Session, *, group_id: str, user_id: str) -> None:
		"""Leave a group (creator cannot leave; last-admin safeguards apply)."""
		# Creator cannot leave the group
		group = self.groups_repo.get(db, group_id=group_id)
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		if str(group.created_by) == str(user_id):
			raise ValueError(Errors.FORBIDDEN)
		m = self.repo.get(db, group_id=group_id, user_id=user_id)
		if m is None:
			return
		self.repo.remove(db, group_id=group_id, user_id=user_id)
		# Last-admin guard if leaver was admin
		if m.role == GroupRoles.ADMIN and self.repo.count_admins(db, group_id=group_id) < 1:
			# re-add as admin (can't leave if last admin)
			self.repo.add(db, group_id=group_id, user_id=user_id, role=GroupRoles.ADMIN)
			raise ValueError(Errors.FORBIDDEN)
		self.logger.info(LogEvents.GROUP_MEMBER_LEFT, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: user_id, Keys.TARGET_USER_ID: user_id, Fields.ROLE: m.role})
		return


