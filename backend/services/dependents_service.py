"""Dependents service: manage dependent records and conversions to accounts."""
from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import date
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import Errors, Keys, Fields, GroupRoles, LogEvents, Roles, Messages
from backend.db.models import User, Group, Dependent
from backend.repositories.dependents_repo import DependentsRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository
from backend.repositories.interfaces import DependentsRepo
from backend.services.utils import ensure_member, ensure_admin_or_guardian
from backend.services.auth_service import hash_password


class DependentsService:
	"""Service for CRUD on dependents within a group, including conversion."""
	def __init__(self, *, repo: DependentsRepo | None = None, memberships: GroupMembershipsRepository | None = None) -> None:
		self.repo: DependentsRepo = repo or DependentsRepository()
		self.memberships = memberships or GroupMembershipsRepository()
		self.logger = logging.getLogger(__name__)

	def create(self, db: Session, *, group_id: str, actor_id: str, full_name: Optional[str], dob: Optional[str], email: Optional[str]) -> Dict[str, Any]:
		"""Create a dependent under a group; actor must be admin or guardian."""
		# Guardian is the actor; admins may create on behalf of themselves as guardian
		ensure_admin_or_guardian(self.memberships, db, group_id=group_id, actor_id=actor_id, guardian_user_id=actor_id)
		parsed_dob: Optional[date] = None
		if dob:
			try:
				parsed_dob = date.fromisoformat(dob)
			except Exception:
				raise ValueError(Errors.INVALID_PAYLOAD)
		norm_email = (email or "").strip().lower() if email else None
		row = self.repo.create(db, group_id=group_id, guardian_user_id=actor_id, full_name=full_name, dob=parsed_dob, email=norm_email)
		self.logger.info(LogEvents.DEPENDENT_CREATED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.DEPENDENT_ID: str(row.id)})
		return {
			Fields.ID: str(row.id),
			Fields.FULL_NAME: row.full_name,
			Keys.DOB: row.dob.isoformat() if row.dob else None,
			Fields.EMAIL: row.email,
			Keys.GUARDIAN_USER_ID: str(row.guardian_user_id),
		}

	def list(self, db: Session, *, group_id: str, actor_id: str, limit: int, offset: int) -> Dict[str, Any]:
		"""List dependents for a group (any group member)."""
		# Any group member can list dependents
		ensure_member(self.memberships, db, group_id=group_id, actor_id=actor_id)
		total = self.repo.count_by_group(db, group_id=group_id)
		rows = self.repo.list_by_group_paginated(db, group_id=group_id, limit=limit, offset=offset)
		items = [
			{
				Fields.ID: str(r.id),
				Fields.FULL_NAME: r.full_name,
				Keys.DOB: r.dob.isoformat() if r.dob else None,
				Fields.EMAIL: r.email,
				Keys.GUARDIAN_USER_ID: str(r.guardian_user_id),
			}
			for r in rows
		]
		return {Keys.ITEMS: items, Keys.TOTAL: total}

	def delete(self, db: Session, *, group_id: str, actor_id: str, dependent_id: str) -> None:
		"""Soft-delete a dependent (admin or guardian)."""
		row = self.repo.get(db, dependent_id=dependent_id)
		if row is None or str(row.group_id) != str(group_id):
			return
		# Admin or guardian can delete
		ensure_admin_or_guardian(self.memberships, db, group_id=group_id, actor_id=actor_id, guardian_user_id=str(row.guardian_user_id))
		self.repo.soft_delete(db, dependent=row)
		self.logger.info(LogEvents.DEPENDENT_DELETED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.DEPENDENT_ID: str(row.id)})
		return

	def convert_to_account(self, db: Session, *, group_id: str, actor_id: str, dependent_id: str, email: Optional[str]) -> Dict[str, Any]:
		"""Convert a dependent into a full user account and add to the group."""
		row = self.repo.get(db, dependent_id=dependent_id)
		if row is None or str(row.group_id) != str(group_id):
			raise ValueError(Errors.USER_NOT_FOUND)
		# Admin or guardian can convert
		ensure_admin_or_guardian(self.memberships, db, group_id=group_id, actor_id=actor_id, guardian_user_id=str(row.guardian_user_id))
		target_email = (row.email or email or "").strip().lower()
		if not target_email:
			raise ValueError(Errors.INVALID_PAYLOAD)
		# Create or get user
		user = db.scalar(select(User).where(User.email == target_email))
		if user is None:
			user = User(
				username=target_email,
				email=target_email,
				password_hash=hash_password("TempPassw0rd!"),
				role=Roles.CAREGIVER,
				full_name=row.full_name,
				corpus_uri=f"user://{target_email}/corpus",
				chat_history_uri=None,
			)
			db.add(user)
			db.commit()
			db.refresh(user)
		# Add membership as member
		self.memberships.add(db, group_id=str(group_id), user_id=str(user.id), role=GroupRoles.MEMBER)
		# Soft-delete dependent record after conversion
		self.repo.soft_delete(db, dependent=row)
		self.logger.info(LogEvents.DEPENDENT_CONVERTED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.DEPENDENT_ID: str(row.id), Keys.USER_ID: str(user.id)})
		return {Keys.MESSAGE: Messages.GROUP_MEMBER_ADDED, Keys.USER_ID: str(user.id)}


