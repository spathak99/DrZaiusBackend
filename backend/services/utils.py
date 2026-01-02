"""Service utilities: group membership checks for access control."""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.core.constants import Errors, GroupRoles
from backend.repositories.interfaces import MembershipsRepo


def ensure_member(memberships: MembershipsRepo, db: Session, *, group_id: str, actor_id: str) -> None:
	"""Ensure the actor is at least a member of the specified group."""
	m = memberships.get(db, group_id=group_id, user_id=actor_id)
	if m is None:
		raise ValueError(Errors.FORBIDDEN)


def ensure_admin(memberships: MembershipsRepo, db: Session, *, group_id: str, actor_id: str) -> None:
	"""Ensure the actor is an admin of the specified group."""
	m = memberships.get(db, group_id=group_id, user_id=actor_id)
	if m is None or m.role != GroupRoles.ADMIN:
		raise ValueError(Errors.FORBIDDEN)


def ensure_admin_or_guardian(memberships: MembershipsRepo, db: Session, *, group_id: str, actor_id: str, guardian_user_id: str | None) -> None:
	"""Ensure the actor is an admin, or the guardian for the dependent within the group."""
	m = memberships.get(db, group_id=group_id, user_id=actor_id)
	if m is None:
		raise ValueError(Errors.FORBIDDEN)
	if m.role == GroupRoles.ADMIN:
		return
	if guardian_user_id is not None and str(guardian_user_id) == str(actor_id):
		return
	raise ValueError(Errors.FORBIDDEN)


