from __future__ import annotations

from typing import Optional, List, Protocol
from sqlalchemy.orm import Session

from backend.db.models import Invitation, RecipientCaregiverAccess


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


