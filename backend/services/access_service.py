from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.constants import Messages, Errors, Fields, Keys
from backend.db.models import User
from backend.repositories.interfaces import AccessRepo
from backend.repositories.access_repo import AccessRepository


class AccessService:
	def __init__(self, repo: AccessRepo | None = None) -> None:
		self.repo: AccessRepo = repo or AccessRepository()

	def assign(self, db: Session, *, recipient_id: str, caregiver_id: str, access_level: Optional[str]) -> Dict[str, Any]:
		recipient = db.scalar(select(User).where(User.id == recipient_id))
		if recipient is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		caregiver = db.scalar(select(User).where(User.id == caregiver_id))
		if caregiver is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		row = self.repo.upsert(db, recipient_id=recipient_id, caregiver_id=caregiver_id, access_level=access_level)
		return {
			Keys.MESSAGE: Messages.CAREGIVER_ASSIGNED,
			Keys.RECIPIENT_ID: str(recipient_id),
			Keys.CAREGIVER_ID: str(caregiver_id),
			Fields.ACCESS_LEVEL: row.access_level,
		}

	def revoke(self, db: Session, *, recipient_id: str, caregiver_id: str) -> None:
		self.repo.delete(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		return

	def update(self, db: Session, *, recipient_id: str, caregiver_id: str, access_level: str) -> Dict[str, Any]:
		row = self.repo.get(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		if row is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		row.access_level = access_level
		db.commit()
		return {
			Keys.MESSAGE: Messages.ACCESS_UPDATED,
			Keys.RECIPIENT_ID: str(recipient_id),
			Keys.CAREGIVER_ID: str(caregiver_id),
			Fields.ACCESS_LEVEL: row.access_level,
		}

	def list_recipient_caregivers(self, db: Session, *, recipient_id: str) -> Dict[str, Any]:
		rows = self.repo.list_for_recipient(db, recipient_id=recipient_id)
		items = [{Keys.CAREGIVER_ID: r.caregiver_id, Fields.ACCESS_LEVEL: r.access_level} for r in rows]
		return {Keys.RECIPIENT_ID: recipient_id, Keys.ITEMS: items}

	def list_caregiver_recipients(self, db: Session, *, caregiver_id: str) -> Dict[str, Any]:
		rows = self.repo.list_for_caregiver(db, caregiver_id=caregiver_id)
		items = [{Keys.RECIPIENT_ID: r.recipient_id, Fields.ACCESS_LEVEL: r.access_level} for r in rows]
		return {Keys.CAREGIVER_ID: caregiver_id, Keys.ITEMS: items}

	def get_caregiver_recipient(self, db: Session, *, caregiver_id: str, recipient_id: str) -> Dict[str, Any]:
		row = self.repo.get(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		if row is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		return {Keys.CAREGIVER_ID: caregiver_id, Keys.RECIPIENT_ID: recipient_id, Fields.ACCESS_LEVEL: row.access_level}


