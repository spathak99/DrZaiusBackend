from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base, uuid_pk, ts_created, ts_updated, (
	EMAIL_MAX_LEN, ROLE_MAX_LEN, FULL_NAME_MAX_LEN, INVITATION_STATUS_MAX_LEN
)
from backend.core.constants import Tables, Fields
from backend.schemas.common import InvitationStatus


class Invitation(Base):
	"""Invitation linking caregivers and recipients, optionally by email prior to signup."""
	__tablename__ = Tables.INVITATIONS

	id: Mapped[uuid.UUID] = uuid_pk()
	caregiver_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
	recipient_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
	status: Mapped[str] = mapped_column(String(INVITATION_STATUS_MAX_LEN), default=InvitationStatus.pending.value)
	# 'sent_by' indicates who initiated the invitation: 'caregiver' or 'recipient'
	sent_by: Mapped[Optional[str]] = mapped_column(String(ROLE_MAX_LEN), nullable=True)
	# When the target user doesn't exist yet, persist their email (and optional name)
	invited_email: Mapped[Optional[str]] = mapped_column(String(EMAIL_MAX_LEN), nullable=True)
	invited_full_name: Mapped[Optional[str]] = mapped_column(String(FULL_NAME_MAX_LEN), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


