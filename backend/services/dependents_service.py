from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import date
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import Errors, Keys, Fields, GroupRoles, LogEvents
from backend.db.models import User, Group, Dependent
from backend.repositories.dependents_repo import DependentsRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository
from backend.repositories.interfaces import DependentsRepo


class DependentsService:
	def __init__(self, *, repo: DependentsRepo | None = None, memberships: GroupMembershipsRepository | None = None) -> None:
		self.repo: DependentsRepo = repo or DependentsRepository()
		self.memberships = memberships or GroupMembershipsRepository()
		self.logger = logging.getLogger(__name__)

	def _ensure_admin_or_guardian(self, db: Session, *, group_id: str, actor_id: str, guardian_user_id: Optional[str] = None) -> None:
		m = self.memberships.get(db, group_id=group_id, user_id=actor_id)
		if m is None:
			raise ValueError(Errors.FORBIDDEN)
		if m.role == GroupRoles.ADMIN:
			return
		# Non-admins must be guardian to act
		if guardian_user_id is not None and str(guardian_user_id) == str(actor_id):
			return
		raise ValueError(Errors.FORBIDDEN)

	def create(self, db: Session, *, group_id: str, actor_id: str, full_name: Optional[str], dob: Optional[str], email: Optional[str]) -> Dict[str, Any]:
		# Guardian is the actor; admins may create on behalf of themselves as guardian
		self._ensure_admin_or_guardian(db, group_id=group_id, actor_id=actor_id, guardian_user_id=actor_id)
		parsed_dob: Optional[date] = None
		if dob:
			try:
				parsed_dob = date.fromisoformat(dob)
			except Exception:
				raise ValueError(Errors.INVALID_PAYLOAD)
		row = self.repo.create(db, group_id=group_id, guardian_user_id=actor_id, full_name=full_name, dob=parsed_dob, email=email)
		self.logger.info(LogEvents.DEPENDENT_CREATED, extra={"groupId": group_id, "actorId": actor_id, "dependentId": str(row.id)})
		return {
			Fields.ID: str(row.id),
			Fields.FULL_NAME: row.full_name,
			"dob": row.dob.isoformat() if row.dob else None,
			Fields.EMAIL: row.email,
			"guardian_user_id": str(row.guardian_user_id),
		}

	def list(self, db: Session, *, group_id: str, actor_id: str, limit: int, offset: int) -> Dict[str, Any]:
		# Any group member can list dependents
		m = self.memberships.get(db, group_id=group_id, user_id=actor_id)
		if m is None:
			raise ValueError(Errors.FORBIDDEN)
		total = self.repo.count_by_group(db, group_id=group_id)
		rows = self.repo.list_by_group_paginated(db, group_id=group_id, limit=limit, offset=offset)
		items = [
			{
				Fields.ID: str(r.id),
				Fields.FULL_NAME: r.full_name,
				"dob": r.dob.isoformat() if r.dob else None,
				Fields.EMAIL: r.email,
				"guardian_user_id": str(r.guardian_user_id),
			}
			for r in rows
		]
		return {Keys.ITEMS: items, Keys.TOTAL: total}

	def delete(self, db: Session, *, group_id: str, actor_id: str, dependent_id: str) -> None:
		row = self.repo.get(db, dependent_id=dependent_id)
		if row is None or str(row.group_id) != str(group_id):
			return
		# Admin or guardian can delete
		self._ensure_admin_or_guardian(db, group_id=group_id, actor_id=actor_id, guardian_user_id=str(row.guardian_user_id))
		self.repo.soft_delete(db, dependent=row)
		self.logger.info(LogEvents.DEPENDENT_DELETED, extra={"groupId": group_id, "actorId": actor_id, "dependentId": str(row.id)})
		return


