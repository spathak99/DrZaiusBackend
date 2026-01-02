"""Access service: manage caregiver access to recipients and files."""
from __future__ import annotations

from typing import Any, Dict, Optional
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.constants import Messages, Errors, Fields, Keys
from backend.db.models import User
from backend.repositories.interfaces import AccessRepo
from backend.repositories.access_repo import AccessRepository


logger = logging.getLogger(__name__)


class AccessService:
	"""Service for granting, updating, revoking, and listing access edges."""
	def __init__(self, repo: AccessRepo | None = None) -> None:
		self.repo: AccessRepo = repo or AccessRepository()
	
	def _map_list_item(self, *, caregiver_id: Optional[str] = None, recipient_id: Optional[str] = None, access_level: Optional[str] = None) -> Dict[str, Any]:
		"""Shape a list item for access edges."""
		item: Dict[str, Any] = {}
		if caregiver_id is not None:
			item[Keys.CAREGIVER_ID] = caregiver_id
		if recipient_id is not None:
			item[Keys.RECIPIENT_ID] = recipient_id
		item[Fields.ACCESS_LEVEL] = access_level
		return item

	def _map_action(self, message: str, *, recipient_id: str, caregiver_id: str, access_level: Optional[str]) -> Dict[str, Any]:
		"""Common response payload for access mutations."""
		return {
			Keys.MESSAGE: message,
			Keys.RECIPIENT_ID: recipient_id,
			Keys.CAREGIVER_ID: caregiver_id,
			Fields.ACCESS_LEVEL: access_level,
		}

	def assign(self, db: Session, *, recipient_id: str, caregiver_id: str, access_level: Optional[str]) -> Dict[str, Any]:
		"""Grant caregiver access to a recipient."""
		recipient = db.scalar(select(User).where(User.id == recipient_id))
		if recipient is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		caregiver = db.scalar(select(User).where(User.id == caregiver_id))
		if caregiver is None:
			raise ValueError(Errors.USER_NOT_FOUND)
		row = self.repo.upsert(db, recipient_id=recipient_id, caregiver_id=caregiver_id, access_level=access_level)
		logger.info("caregiver assigned", extra={Keys.RECIPIENT_ID: recipient_id, Keys.CAREGIVER_ID: caregiver_id})
		return self._map_action(Messages.CAREGIVER_ASSIGNED, recipient_id=str(recipient_id), caregiver_id=str(caregiver_id), access_level=row.access_level)

	def revoke(self, db: Session, *, recipient_id: str, caregiver_id: str) -> None:
		"""Revoke caregiver access to a recipient."""
		self.repo.delete(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		return

	def update(self, db: Session, *, recipient_id: str, caregiver_id: str, access_level: str) -> Dict[str, Any]:
		"""Update a caregiver's access level for a recipient."""
		row = self.repo.get(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		if row is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		row.access_level = access_level
		db.commit()
		logger.info("access updated", extra={Keys.RECIPIENT_ID: recipient_id, Keys.CAREGIVER_ID: caregiver_id})
		return self._map_action(Messages.ACCESS_UPDATED, recipient_id=str(recipient_id), caregiver_id=str(caregiver_id), access_level=row.access_level)

	def list_recipient_caregivers(self, db: Session, *, recipient_id: str) -> Dict[str, Any]:
		"""List caregivers who have access to a recipient."""
		rows = self.repo.list_for_recipient(db, recipient_id=recipient_id)
		items = [self._map_list_item(caregiver_id=str(r.caregiver_id), access_level=r.access_level) for r in rows]
		return {Keys.RECIPIENT_ID: recipient_id, Keys.ITEMS: items}

	def list_caregiver_recipients(self, db: Session, *, caregiver_id: str) -> Dict[str, Any]:
		"""List recipients a caregiver has access to."""
		rows = self.repo.list_for_caregiver(db, caregiver_id=caregiver_id)
		items = [self._map_list_item(recipient_id=str(r.recipient_id), access_level=r.access_level) for r in rows]
		return {Keys.CAREGIVER_ID: caregiver_id, Keys.ITEMS: items}

	def get_caregiver_recipient(self, db: Session, *, caregiver_id: str, recipient_id: str) -> Dict[str, Any]:
		"""Get access details for a specific caregiver-recipient edge."""
		row = self.repo.get(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		if row is None:
			raise ValueError(Errors.RECIPIENT_NOT_FOUND)
		return {Keys.CAREGIVER_ID: caregiver_id, Keys.RECIPIENT_ID: recipient_id, Fields.ACCESS_LEVEL: row.access_level}


