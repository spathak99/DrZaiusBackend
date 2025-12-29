from __future__ import annotations

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from backend.db.models import GroupPaymentCode
from backend.core.constants import PaymentCodeStatus


class PaymentCodesRepository:
	def create(self, db: Session, *, group_id: str, code: str, created_by: str, expires_at: Optional[datetime]) -> GroupPaymentCode:
		row = GroupPaymentCode(group_id=group_id, code=code, created_by=created_by, expires_at=expires_at, status=PaymentCodeStatus.ACTIVE)
		db.add(row)
		db.commit()
		db.refresh(row)
		return row

	def get_by_code(self, db: Session, *, code: str) -> Optional[GroupPaymentCode]:
		return db.scalar(select(GroupPaymentCode).where(GroupPaymentCode.code == code))

	def list_for_group(self, db: Session, *, group_id: str) -> List[GroupPaymentCode]:
		return db.scalars(select(GroupPaymentCode).where(GroupPaymentCode.group_id == group_id)).all()

	def void(self, db: Session, *, row: GroupPaymentCode) -> GroupPaymentCode:
		row.status = PaymentCodeStatus.EXPIRED
		db.commit()
		db.refresh(row)
		return row

	def mark_redeemed(self, db: Session, *, row: GroupPaymentCode, user_id: str) -> GroupPaymentCode:
		row.status = PaymentCodeStatus.REDEEMED
		row.redeemed_by = user_id
		row.redeemed_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(row)
		return row


