from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import RecipientCaregiverAccess


class AccessRepository:
	def get(self, db: Session, *, recipient_id, caregiver_id) -> Optional[RecipientCaregiverAccess]:
		return db.scalar(
			select(RecipientCaregiverAccess).where(
				RecipientCaregiverAccess.recipient_id == recipient_id,
				RecipientCaregiverAccess.caregiver_id == caregiver_id,
			)
		)

	def list_for_recipient(self, db: Session, *, recipient_id) -> list[RecipientCaregiverAccess]:
		return db.scalars(select(RecipientCaregiverAccess).where(RecipientCaregiverAccess.recipient_id == recipient_id)).all()

	def list_for_caregiver(self, db: Session, *, caregiver_id) -> list[RecipientCaregiverAccess]:
		return db.scalars(select(RecipientCaregiverAccess).where(RecipientCaregiverAccess.caregiver_id == caregiver_id)).all()

	def upsert(self, db: Session, *, recipient_id, caregiver_id, access_level: Optional[str]) -> RecipientCaregiverAccess:
		existing = self.get(db, recipient_id=recipient_id, caregiver_id=caregiver_id)
		if existing:
			existing.access_level = access_level or existing.access_level
			db.commit()
			db.refresh(existing)
			return existing
		row = RecipientCaregiverAccess(recipient_id=recipient_id, caregiver_id=caregiver_id, access_level=access_level)
		db.add(row)
		db.commit()
		db.refresh(row)
		return row

	def delete(self, db: Session, *, recipient_id, caregiver_id) -> None:
		rows = db.scalars(
			select(RecipientCaregiverAccess).where(
				RecipientCaregiverAccess.recipient_id == recipient_id,
				RecipientCaregiverAccess.caregiver_id == caregiver_id,
			)
		).all()
		for row in rows:
			db.delete(row)
		db.commit()
		return


