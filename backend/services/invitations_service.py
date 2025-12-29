from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import (
	Keys,
	Fields,
	Roles,
	Messages,
	InvitationStatus,
	DeepLink,
	Errors,
)
from backend.db.models import User, Invitation, RecipientCaregiverAccess
from backend.repositories.invitations_repo import InvitationsRepository
from backend.services.invite_signing import sign_invite
from backend.services.email_service import send_invite_email


class InvitationsService:
	def __init__(self) -> None:
		self.repo = InvitationsRepository()

	def _sender(self, user: Optional[User]) -> Dict[str, Optional[str]]:
		return {
			Keys.SENDER_ID: str(user.id) if user else None,
			Keys.SENDER_EMAIL: user.email if user else None,
			Keys.SENDER_FULL_NAME: user.full_name if user else None,
		}

	def _accept_url(self, payload: Dict[str, Any]) -> Optional[str]:
		try:
			token = sign_invite(payload)
			return f"{DeepLink.SCHEME}://{DeepLink.INVITE_ACCEPT_PATH}?token={token}"
		except Exception:
			return None

	def send_from_caregiver(self, db: Session, *, caregiver_id: str, email: str) -> Dict[str, Any]:
		caregiver = db.scalar(select(User).where(User.id == caregiver_id))
		if caregiver is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		recipient = db.scalar(select(User).where(User.email == email))
		inv = self.repo.create(
			db,
			caregiver_id=caregiver.id,
			recipient_id=(recipient.id if recipient else None),
			invited_email=(None if recipient else str(email)),
			sent_by=Roles.CAREGIVER,
		)
		accept_url = self._accept_url({"invitationId": str(inv.id), "role": Roles.RECIPIENT, "recipientId": str(recipient.id) if recipient else None})
		send_invite_email(to_email=str(email), accept_url=accept_url)
		return {
			Fields.ID: str(inv.id),
			Keys.CAREGIVER_ID: str(inv.caregiver_id),
			Keys.RECIPIENT_ID: str(inv.recipient_id) if inv.recipient_id else None,
			Keys.STATUS: inv.status,
			Keys.SENT_BY: inv.sent_by,
			**self._sender(caregiver),
			Keys.ACCEPT_URL: accept_url,
		}

	def send_from_recipient(self, db: Session, *, recipient_id: str, email: str) -> Dict[str, Any]:
		recipient = db.scalar(select(User).where(User.id == recipient_id))
		if recipient is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		caregiver = db.scalar(select(User).where(User.email == email))
		inv = self.repo.create(
			db,
			caregiver_id=(caregiver.id if caregiver else None),
			recipient_id=recipient.id,
			invited_email=(None if caregiver else str(email)),
			sent_by=Roles.RECIPIENT,
		)
		accept_url = self._accept_url({"invitationId": str(inv.id), "role": Roles.CAREGIVER, "caregiverId": str(caregiver.id) if caregiver else None})
		send_invite_email(to_email=str(email), accept_url=accept_url)
		return {
			Fields.ID: str(inv.id),
			Keys.CAREGIVER_ID: str(inv.caregiver_id) if inv.caregiver_id else None,
			Keys.RECIPIENT_ID: str(inv.recipient_id) if inv.recipient_id else None,
			Keys.STATUS: inv.status,
			Keys.SENT_BY: inv.sent_by,
			**self._sender(recipient),
			Keys.ACCEPT_URL: accept_url,
		}

	def list_for_caregiver(self, db: Session, *, caregiver_id: str) -> List[Dict[str, Any]]:
		caregiver = db.scalar(select(User).where(User.id == caregiver_id))
		if caregiver is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		invites = self.repo.list_pending_for_caregiver(db, caregiver_id, caregiver.email)
		items: List[Dict[str, Any]] = []
		for inv in invites:
			other = db.scalar(
				select(User).where(User.id == (inv.caregiver_id if inv.sent_by == Roles.CAREGIVER else inv.recipient_id))
			)
			items.append(
				{
					Fields.ID: str(inv.id),
					Keys.CAREGIVER_ID: str(inv.caregiver_id) if inv.caregiver_id else None,
					Keys.RECIPIENT_ID: str(inv.recipient_id) if inv.recipient_id else None,
					Keys.STATUS: inv.status,
					Keys.SENT_BY: inv.sent_by,
					**self._sender(other),
				}
			)
		return items

	def list_for_recipient(self, db: Session, *, recipient_id: str) -> List[Dict[str, Any]]:
		recipient = db.scalar(select(User).where(User.id == recipient_id))
		if recipient is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		invites = self.repo.list_pending_for_recipient(db, recipient_id, recipient.email)
		items: List[Dict[str, Any]] = []
		for inv in invites:
			other = db.scalar(
				select(User).where(User.id == (inv.caregiver_id if inv.sent_by == Roles.CAREGIVER else inv.recipient_id))
			)
			items.append(
				{
					Fields.ID: str(inv.id),
					Keys.CAREGIVER_ID: str(inv.caregiver_id) if inv.caregiver_id else None,
					Keys.RECIPIENT_ID: str(inv.recipient_id) if inv.recipient_id else None,
					Keys.STATUS: inv.status,
					Keys.SENT_BY: inv.sent_by,
					**self._sender(other),
				}
			)
		return items

	def list_sent_by_recipient(self, db: Session, *, recipient_id: str) -> List[Dict[str, Any]]:
		recipient = db.scalar(select(User).where(User.id == recipient_id))
		if recipient is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		invs = db.scalars(
			select(Invitation).where(
				Invitation.recipient_id == recipient_id,
				Invitation.status == InvitationStatus.PENDING,
				Invitation.sent_by == Roles.RECIPIENT,
			)
		).all()
		return [
			{
				Fields.ID: str(i.id),
				Keys.CAREGIVER_ID: str(i.caregiver_id),
				Keys.RECIPIENT_ID: str(i.recipient_id),
				Keys.STATUS: i.status,
				Keys.SENT_BY: i.sent_by,
				**self._sender(recipient),
			}
			for i in invs
		]

	def accept_by_token(self, db: Session, *, token: str) -> Dict[str, Any]:
		from backend.services.invite_signing import verify_invite

		if not token:
			raise ValueError(Errors.MISSING_TOKEN)
		try:
			data = verify_invite(token)
		except ValueError:
			raise ValueError(Errors.INVALID_TOKEN)
		invitation_id = data.get("invitationId")
		role = data.get("role")
		if not invitation_id or role not in (Roles.RECIPIENT, Roles.CAREGIVER):
			raise ValueError(Errors.INVALID_PAYLOAD)
		try:
			inv_uuid = uuid.UUID(str(invitation_id))
		except Exception:
			raise ValueError(Errors.USER_NOT_FOUND)
		inv = self.repo.get_pending_by_id(db, inv_uuid)
		if inv is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		if role == Roles.RECIPIENT and inv.recipient_id is None:
			raise ValueError(Errors.RECIPIENT_NOT_REGISTERED)
		if role == Roles.CAREGIVER and inv.caregiver_id is None:
			raise ValueError(Errors.CAREGIVER_NOT_REGISTERED)
		# Accept and create access edge
		self.repo.set_status(db, inv, InvitationStatus.ACCEPTED)
		access = RecipientCaregiverAccess(recipient_id=inv.recipient_id, caregiver_id=inv.caregiver_id)
		db.add(access)
		db.commit()
		return {Keys.MESSAGE: Messages.INVITATION_ACCEPTED, Keys.INVITATION_ID: str(inv.id)}


