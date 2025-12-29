from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import Invitation
from backend.core.constants import InvitationStatus


class InvitationsRepository:
	def get_pending_by_id(self, db: Session, invitation_id) -> Optional[Invitation]:
		return db.scalar(
			select(Invitation).where(Invitation.id == invitation_id, Invitation.status == InvitationStatus.PENDING)
		)

	def list_pending_for_caregiver(self, db: Session, caregiver_id, caregiver_email: str) -> list[Invitation]:
		return db.scalars(
			select(Invitation).where(
				Invitation.status == InvitationStatus.PENDING,
				(Invitation.caregiver_id == caregiver_id) | (Invitation.invited_email == caregiver_email),
			)
		).all()

	def list_pending_for_recipient(self, db: Session, recipient_id, recipient_email: str) -> list[Invitation]:
		return db.scalars(
			select(Invitation).where(
				Invitation.status == InvitationStatus.PENDING,
				(Invitation.recipient_id == recipient_id) | (Invitation.invited_email == recipient_email),
			)
		).all()

	def create(
		self,
		db: Session,
		*,
		caregiver_id,
		recipient_id,
		invited_email: Optional[str],
		sent_by: str,
	) -> Invitation:
		inv = Invitation(
			caregiver_id=caregiver_id,
			recipient_id=recipient_id,
			invited_email=invited_email,
			status=InvitationStatus.PENDING,
		)
		inv.sent_by = sent_by
		db.add(inv)
		db.commit()
		db.refresh(inv)
		return inv

	def set_status(self, db: Session, inv: Invitation, status: str) -> Invitation:
		inv.status = status
		db.commit()
		db.refresh(inv)
		return inv


