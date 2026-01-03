from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base, uuid_pk, ts_created, ts_updated, (
	USERNAME_MAX_LEN, EMAIL_MAX_LEN, PASSWORD_HASH_MAX_LEN, ROLE_MAX_LEN,
	CORPUS_URI_MAX_LEN, CHAT_HISTORY_URI_MAX_LEN, PROJECT_ID_MAX_LEN,
	BUCKET_NAME_MAX_LEN, FULL_NAME_MAX_LEN, PHONE_NUMBER_MAX_LEN,
	COUNTRY_MAX_LEN, AVATAR_URI_MAX_LEN, ACCESS_LEVEL_MAX_LEN
)
from backend.core.constants import Tables, Fields


class User(Base):
	"""Application user with auth credentials, profile fields, and relations."""
	__tablename__ = Tables.USERS

	id: Mapped[uuid.UUID] = uuid_pk()
	username: Mapped[str] = mapped_column(String(USERNAME_MAX_LEN), unique=True, index=True, nullable=False)
	email: Mapped[str] = mapped_column(String(EMAIL_MAX_LEN), unique=True, index=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LEN), nullable=False)
	role: Mapped[str] = mapped_column(String(ROLE_MAX_LEN), nullable=False)
	corpus_uri: Mapped[str] = mapped_column(String(CORPUS_URI_MAX_LEN), nullable=False)
	chat_history_uri: Mapped[Optional[str]] = mapped_column(String(CHAT_HISTORY_URI_MAX_LEN), nullable=True)
	account_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
	group_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="SET NULL"), nullable=True)
	gcp_project_id: Mapped[Optional[str]] = mapped_column(String(PROJECT_ID_MAX_LEN), nullable=True)
	temp_bucket: Mapped[Optional[str]] = mapped_column(String(BUCKET_NAME_MAX_LEN), nullable=True)
	payment_info: Mapped[Optional[dict]] = mapped_column(sa.dialects.postgresql.JSONB, nullable=True)  # type: ignore
	# Profile fields (for mobile UX)
	full_name: Mapped[Optional[str]] = mapped_column(String(FULL_NAME_MAX_LEN), nullable=True)
	phone_number: Mapped[Optional[str]] = mapped_column(String(PHONE_NUMBER_MAX_LEN), nullable=True)
	age: Mapped[Optional[int]] = mapped_column(nullable=True)
	country: Mapped[Optional[str]] = mapped_column(String(COUNTRY_MAX_LEN), nullable=True)
	avatar_uri: Mapped[Optional[str]] = mapped_column(String(AVATAR_URI_MAX_LEN), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()

	chats_created: Mapped[List["Chat"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
	groups_memberships: Mapped[List["GroupMembership"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	# Optional read-only convenience to directly access groups
	groups: Mapped[List["Group"]] = relationship(
		"Group",
		secondary=Tables.GROUP_MEMBERSHIPS,
		primaryjoin="User.id==GroupMembership.user_id",
		secondaryjoin="Group.id==GroupMembership.group_id",
		viewonly=True,
	)


class RecipientCaregiverAccess(Base):
	"""Edge granting a caregiver access to a recipient with optional access level."""
	__tablename__ = Tables.RECIPIENT_CAREGIVER_ACCESS

	id: Mapped[uuid.UUID] = uuid_pk()
	recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	access_level: Mapped[Optional[str]] = mapped_column(String(ACCESS_LEVEL_MAX_LEN), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


