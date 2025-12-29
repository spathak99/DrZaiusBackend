from __future__ import annotations

import secrets
import base64
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.core.constants import Errors, Keys, Messages, GroupRoles, PaymentCodeStatus
from backend.repositories.payment_codes_repo import PaymentCodesRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository
from backend.repositories.groups_repo import GroupsRepository


class PaymentCodesService:
	def __init__(self) -> None:
		self.repo = PaymentCodesRepository()
		self.members = GroupMembershipsRepository()
		self.groups = GroupsRepository()

	def _ensure_admin(self, db: Session, *, group_id: str, actor_id: str) -> None:
		m = self.members.get(db, group_id=group_id, user_id=actor_id)
		if m is None or m.role != GroupRoles.ADMIN:
			raise ValueError(Errors.FORBIDDEN)

	def _gen_code(self, length: int = 20) -> str:
		# URL-safe token
		return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode("utf-8").rstrip("=")

	def create_code(self, db: Session, *, group_id: str, actor_id: str, ttl_minutes: Optional[int] = None) -> Dict[str, Any]:
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		expires_at = None
		if ttl_minutes and ttl_minutes > 0:
			expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
		code = self._gen_code(12)
		row = self.repo.create(db, group_id=group_id, code=code, created_by=actor_id, expires_at=expires_at)
		return {Keys.CODE: row.code, Keys.STATUS: row.status, Keys.EXPIRES_AT: row.expires_at}

	def list_codes(self, db: Session, *, group_id: str, actor_id: str) -> List[Dict[str, Any]]:
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		rows = self.repo.list_for_group(db, group_id=group_id)
		return [{Keys.CODE: r.code, Keys.STATUS: r.status, Keys.EXPIRES_AT: r.expires_at, Keys.REDEEMED_BY: str(r.redeemed_by) if r.redeemed_by else None} for r in rows]

	def void_code(self, db: Session, *, group_id: str, actor_id: str, code: str) -> Dict[str, Any]:
		self._ensure_admin(db, group_id=group_id, actor_id=actor_id)
		row = self.repo.get_by_code(db, code=code)
		if row is None or str(row.group_id) != str(group_id):
			raise ValueError(Errors.PAYMENT_CODE_NOT_FOUND)
		self.repo.void(db, row=row)
		return {Keys.CODE: code, Keys.STATUS: "expired"}

	def redeem(self, db: Session, *, code: str, user_id: str) -> Dict[str, Any]:
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
		return {Keys.MESSAGE: Messages.PAYMENT_CODE_REDEEMED, Keys.CODE: code}


