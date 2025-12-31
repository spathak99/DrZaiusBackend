from __future__ import annotations

from typing import List, Optional
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.db.models import Dependent


class DependentsRepository:
	def create(self, db: Session, *, group_id: str, guardian_user_id: str, full_name: Optional[str], dob: Optional[date], email: Optional[str]) -> Dependent:
		row = Dependent(group_id=group_id, guardian_user_id=guardian_user_id, full_name=full_name, dob=dob, email=email)
		db.add(row)
		db.commit()
		db.refresh(row)
		return row

	def get(self, db: Session, *, dependent_id: str) -> Optional[Dependent]:
		return db.scalar(select(Dependent).where(Dependent.id == dependent_id))

	def list_by_group_paginated(self, db: Session, *, group_id: str, limit: int, offset: int) -> List[Dependent]:
		return db.scalars(
			select(Dependent)
			.where(Dependent.group_id == group_id, Dependent.deleted_at.is_(None))
			.order_by(Dependent.created_at)
			.limit(limit)
			.offset(offset)
		).all()

	def count_by_group(self, db: Session, *, group_id: str) -> int:
		return int(
			db.scalar(
				select(func.count()).select_from(Dependent).where(Dependent.group_id == group_id, Dependent.deleted_at.is_(None))
			)
			or 0
		)

	def soft_delete(self, db: Session, *, dependent: Dependent) -> None:
		dependent.deleted_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(dependent)


