"""Payment codes service: manage creation, listing, voiding, and redemption of codes."""
from __future__ import annotations

import secrets
import base64
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.core.constants import Errors, Keys, Messages, GroupRoles, PaymentCodeStatus, LogEvents, PaymentCodes
from backend.repositories.payment_codes_repo import PaymentCodesRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository
from backend.repositories.groups_repo import GroupsRepository


class PaymentCodesService:
	"""Service to create and administer group-bound payment codes."""
	def __init__(
		self,
		*,
		repo: PaymentCodesRepository | None = None,
		members: GroupMembershipsRepository | None = None,
		groups: GroupsRepository | None = None,
	) -> None:
		self.repo = repo or PaymentCodesRepository()
		self.members = members or GroupMembershipsRepository()
		self.groups = groups or GroupsRepository()
		self.logger = logging.getLogger(__name__)

	def _ensure_admin(self, db: Session, *, group_id: str, actor_id: str) -> None:
		"""Ensure the actor is an admin of the group."""
		m = self.members.get(db, group_id=group_id, user_id=actor_id)
		if m is None or m.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)

	def _gen_code(self, length: int = PaymentCodes.CODE_BYTES) -> str:
		# URL-safe token
		return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode("utf-8").rstrip("=")

	def create_code(self, db: Session, *, group_id: str, actor_id: str, ttl_minutes: Optional[int] = None) -> Dict[str, Any]:
		"""Create a new payment code, optionally with an expiry TTL."""
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		expires_at = None
		if ttl_minutes and ttl_minutes > 0:
			expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
		code = self._gen_code(PaymentCodes.CODE_BYTES)
		row = self.repo.create(db, group_id=group_id, code=code, created_by=actor_id, expires_at=expires_at)
		self.logger.info(LogEvents.PAYMENT_CODE_CREATED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.CODE: code})
		return {Keys.CODE: row.code, Keys.STATUS: row.status, Keys.EXPIRES_AT: row.expires_at}

	def list_codes(self, db: Session, *, group_id: str, actor_id: str, limit: int | None = None, offset: int | None = None) -> Dict[str, Any]:
		"""List payment codes for a group, optionally paginated."""
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		# pagination (optional)
		if limit is not None and offset is not None:
			total = self.repo.count_for_group(db, group_id=group_id)
			rows = self.repo.list_for_group_paginated(db, group_id=group_id, limit=limit, offset=offset)
		else:
			rows = self.repo.list_for_group(db, group_id=group_id)
			total = len(rows)
		items = [{Keys.CODE: r.code, Keys.STATUS: r.status, Keys.EXPIRES_AT: r.expires_at, Keys.REDEEMED_BY: str(r.redeemed_by) if r.redeemed_by else None} for r in rows]
		return {Keys.ITEMS: items, Keys.TOTAL: total}

	def void_code(self, db: Session, *, group_id: str, actor_id: str, code: str) -> Dict[str, Any]:
		"""Void a payment code (admin only)."""
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		row = self.repo.get_by_code(db, code=code)
		if row is None or str(row.group_id) != str(group_id):
			raise ValueError(Errors.PAYMENT_CODE_NOT_FOUND)
		self.repo.void(db, row=row)
		self.logger.info(LogEvents.PAYMENT_CODE_VOIDED, extra={Keys.GROUP_ID: group_id, Keys.ACTOR_ID: actor_id, Keys.CODE: code})
		return {Keys.CODE: code, Keys.STATUS: PaymentCodeStatus.EXPIRED}

	def redeem(self, db: Session, *, code: str, user_id: str) -> Dict[str, Any]:
		"""Redeem a valid payment code for a user."""
		row = self.repo.get_by_code(db, code=code)
		if row is None:
			raise ValueError(Errors.PAYMENT_CODE_NOT_FOUND)
		if row.status == PaymentCodeStatus.EXPIRED:
			raise ValueError(Errors.PAYMENT_CODE_EXPIRED)
		if row.status == PaymentCodeStatus.REDEEMED:
			raise ValueError(Errors.PAYMENT_CODE_REDEEMED_ALREADY)
		if row.expires_at and row.expires_at < datetime.now(timezone.utc):
			self.repo.void(db, row=row)
			raise ValueError(Errors.PAYMENT_CODE_EXPIRED)
		self.repo.mark_redeemed(db, row=row, user_id=user_id)
		self.logger.info(LogEvents.PAYMENT_CODE_REDEEMED, extra={Keys.GROUP_ID: str(row.group_id), Keys.ACTOR_ID: user_id, Keys.CODE: code})
		return {Keys.MESSAGE: Messages.PAYMENT_CODE_REDEEMED, Keys.CODE: code}


