from __future__ import annotations

from typing import Any, Dict, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
import secrets

from backend.core.constants import Errors, Keys, Fields, Messages, LogEvents, GroupRoles, DeepLink, TokenTypes, Roles
from backend.db.models import User, Group
from backend.repositories.group_member_invites_repo import GroupMemberInvitesRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository
from backend.services.email_service import send_invite_email
from backend.services.invite_signing import sign_invite, verify_invite
from backend.core.settings import get_settings
from backend.services.auth_service import hash_password
from backend.schemas.common import InvitationStatus
from backend.repositories.interfaces import GroupMemberInvitesRepo
from backend.services.utils import ensure_admin


class GroupMemberInvitesService:
	def __init__(self, *, repo: GroupMemberInvitesRepo | None = None, memberships: GroupMembershipsRepository | None = None) -> None:
		self.repo: GroupMemberInvitesRepo = repo or GroupMemberInvitesRepository()
		self.memberships = memberships or GroupMembershipsRepository()
		self.logger = logging.getLogger(__name__)

	def _ensure_admin(self, db: Session, *, group_id: str, actor_id: str) -> None:
		m = self.memberships.get(db, group_id=group_id, user_id=actor_id)
		if m is None or m.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)

	def send(self, db: Session, *, group_id: str, actor_id: str, email: str, full_name: Optional[str]) -> Dict[str, Any]:
		# guard
		ensure_admin(self.memberships, db, group_id=group_id, actor_id=actor_id)
		# idempotent: if user exists, caller should add membership directly. Here we still send invite.
		email = (email or "").strip().lower()
		row = self.repo.get_pending_by_email(db, group_id=group_id, email=email)
		if row is None:
			row = self.repo.create(db, group_id=group_id, invited_email=email, invited_full_name=full_name, invited_by=actor_id)
		# email
		token = sign_invite({Keys.INVITATION_ID: str(row.id), Keys.GROUP_ID: group_id, Fields.EMAIL: email, Keys.TYPE: TokenTypes.GROUP_MEMBER})
		accept_url = f"{DeepLink.SCHEME}://{DeepLink.INVITE_ACCEPT_PATH}?{Keys.TOKEN}={token}"
		send_invite_email(to_email=email, accept_url=accept_url)
		self.logger.info(LogEvents.INVITATION_SENT, extra={"groupId": group_id, "actorId": actor_id, "invitationId": str(row.id), "email": email})
		resp = {
			Fields.ID: str(row.id),
			Keys.INVITED_EMAIL: row.invited_email,
			Keys.INVITED_FULL_NAME: row.invited_full_name,
			Keys.STATUS: row.status,
		}
		# For local testing convenience: include acceptUrl in response if email sending is disabled
		settings = get_settings()
		if not settings.sendgrid_api_key:
			resp[Keys.ACCEPT_URL] = accept_url
		return resp

	def list_pending(self, db: Session, *, group_id: str, limit: int, offset: int) -> Dict[str, Any]:
		total = self.repo.count_pending(db, group_id=group_id)
		rows = self.repo.list_pending_paginated(db, group_id=group_id, limit=limit, offset=offset)
		items = [
			{
				Fields.ID: str(r.id),
				Keys.INVITED_EMAIL: r.invited_email,
				Keys.INVITED_FULL_NAME: r.invited_full_name,
				Keys.STATUS: r.status,
			}
			for r in rows
		]
		return {Keys.ITEMS: items, Keys.TOTAL: total}

	def accept_by_token(self, db: Session, *, token: str) -> Dict[str, Any]:
		if not token:
			raise ValueError(Errors.MISSING_TOKEN)
		try:
			data = verify_invite(token)
		except ValueError:
			raise ValueError(Errors.INVALID_TOKEN)
		invite_id = data.get(Keys.INVITATION_ID)
		group_id = data.get(Keys.GROUP_ID)
		email = (data.get(Fields.EMAIL) or "").strip().lower()
		if not invite_id or not group_id or not email:
			raise ValueError(Errors.INVALID_PAYLOAD)
		invite = self.repo.get(db, invite_id=str(invite_id))
		if invite is None or str(invite.group_id) != str(group_id) or invite.status != InvitationStatus.pending.value:
			raise ValueError(Errors.USER_NOT_FOUND)
		group = db.scalar(select(Group).where(Group.id == group_id))
		if group is None:
			raise ValueError(Errors.GROUP_NOT_FOUND)
		user = db.scalar(select(User).where(User.email == email))
		if user is None:
			user = User(
				username=email,
				email=email,
				password_hash=hash_password(secrets.token_urlsafe(12)),
				role=Roles.CAREGIVER,
				full_name=invite.invited_full_name,
				corpus_uri=f"user://{email}/corpus",
				chat_history_uri=None,
			)
			db.add(user)
			db.commit()
			db.refresh(user)
		self.memberships.add(db, group_id=str(group_id), user_id=str(user.id), role=GroupRoles.MEMBER)
		self.repo.set_status(db, invite=invite, status=InvitationStatus.accepted.value)
		self.logger.info(LogEvents.INVITATION_ACCEPTED, extra={"groupId": str(group_id), "actorEmail": email, "invitationId": str(invite.id)})
		return {Keys.MESSAGE: Messages.INVITATION_ACCEPTED, Keys.GROUP_ID: str(group_id), Fields.USERNAME: user.username}


