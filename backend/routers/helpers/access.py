from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import Errors
from backend.db.models import User, RecipientCaregiverAccess


def assert_can_access_recipient(db: Session, recipient_id: str, current_user: User) -> None:
	"""Allow self or caregivers with an access edge to the recipient."""
	if str(current_user.id) == recipient_id:
		return
	allowed = db.scalar(
		select(RecipientCaregiverAccess).where(
			RecipientCaregiverAccess.recipient_id == recipient_id,
			RecipientCaregiverAccess.caregiver_id == current_user.id,
		)
	)
	if not allowed:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)


