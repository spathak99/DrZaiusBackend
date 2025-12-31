from __future__ import annotations

from typing import Optional, List, Protocol
from sqlalchemy.orm import Session

from backend.db.models import Invitation, RecipientCaregiverAccess, GroupMemberInvite, Dependent


class InvitationsRepo(Protocol):
	def get_pending_by_id(self, db: Session, invitation_id) -> Optional[Invitation]:
		...

	def list_pending_for_caregiver(self, db: Session, caregiver_id, caregiver_email: str) -> List[Invitation]:
		...

	def list_pending_for_recipient(self, db: Session, recipient_id, recipient_email: str) -> List[Invitation]:
		...

	def create(
		self,
		db: Session,
		*,
		caregiver_id,
		recipient_id,
		invited_email: Optional[str],
		sent_by: str,
	) -> Invitation:
		...

	def set_status(self, db: Session, inv: Invitation, status: str) -> Invitation:
		...


class AccessRepo(Protocol):
	def get(self, db: Session, *, recipient_id, caregiver_id) -> Optional[RecipientCaregiverAccess]:
		...

	def list_for_recipient(self, db: Session, *, recipient_id) -> List[RecipientCaregiverAccess]:
		...

	def list_for_caregiver(self, db: Session, *, caregiver_id) -> List[RecipientCaregiverAccess]:
		...

	def upsert(self, db: Session, *, recipient_id, caregiver_id, access_level: Optional[str]) -> RecipientCaregiverAccess:
		...

	def delete(self, db: Session, *, recipient_id, caregiver_id) -> None:
		...


class GroupMemberInvitesRepo(Protocol):
	def create(self, db: Session, *, group_id: str, invited_email: str, invited_full_name: Optional[str], invited_by: str, expires_at=None) -> GroupMemberInvite:
		...

	def get(self, db: Session, *, invite_id: str) -> Optional[GroupMemberInvite]:
		...

	def get_pending_by_email(self, db: Session, *, group_id: str, email: str) -> Optional[GroupMemberInvite]:
		...

	def list_pending_paginated(self, db: Session, *, group_id: str, limit: int, offset: int) -> List[GroupMemberInvite]:
		...

	def count_pending(self, db: Session, *, group_id: str) -> int:
		...

	def set_status(self, db: Session, *, invite: GroupMemberInvite, status: str) -> None:
		...


class DependentsRepo(Protocol):
	def create(self, db: Session, *, group_id: str, guardian_user_id: str, full_name: Optional[str], dob, email: Optional[str]) -> Dependent:
		...

	def get(self, db: Session, *, dependent_id: str) -> Optional[Dependent]:
		...

	def list_by_group_paginated(self, db: Session, *, group_id: str, limit: int, offset: int) -> List[Dependent]:
		...

	def count_by_group(self, db: Session, *, group_id: str) -> int:
		...

	def soft_delete(self, db: Session, *, dependent: Dependent) -> None:
		...


