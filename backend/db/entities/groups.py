from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base, uuid_pk, ts_created, ts_updated, (
	GROUP_NAME_MAX_LEN, GROUP_DESC_MAX_LEN, GROUP_ROLE_MAX_LEN,
	EMAIL_MAX_LEN, FULL_NAME_MAX_LEN
)
from backend.core.constants import Tables, Fields, PaymentCodeStatus
from backend.schemas.common import InvitationStatus
from .user import User


class Group(Base):
	"""Group container for multi-user plans, with an owner and members."""
	__tablename__ = Tables.GROUPS

	id: Mapped[uuid.UUID] = uuid_pk()
	name: Mapped[str] = mapped_column(String(GROUP_NAME_MAX_LEN), index=True)
	description: Mapped[Optional[str]] = mapped_column(String(GROUP_DESC_MAX_LEN), nullable=True)
	created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()

	# Disambiguate relationship to User since there are multiple FKs between users and groups
	owner: Mapped[User] = relationship("User", foreign_keys=[created_by])
	members: Mapped[List["GroupMembership"]] = relationship(back_populates="group", cascade="all, delete-orphan")


class GroupMembership(Base):
	"""Membership edge between a user and a group with a role."""
	__tablename__ = Tables.GROUP_MEMBERSHIPS

	__table_args__ = (
		UniqueConstraint("group_id", "user_id", name="uq_group_membership_group_user"),
		UniqueConstraint("user_id", name="uq_group_membership_user_unique"),
	)
	id: Mapped[uuid.UUID] = uuid_pk()
	group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="CASCADE"))
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}", ondelete="CASCADE"))
	role: Mapped[Optional[str]] = mapped_column(String(GROUP_ROLE_MAX_LEN), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()

	group: Mapped[Group] = relationship(back_populates="members")
	user: Mapped[User] = relationship(back_populates="groups_memberships")


class GroupPaymentCode(Base):
	"""Payment code associated with a group for onboarding and billing flows."""
	__tablename__ = Tables.GROUP_PAYMENT_CODES

	id: Mapped[uuid.UUID] = uuid_pk()
	group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="CASCADE"))
	code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
	status: Mapped[str] = mapped_column(String(20), default=PaymentCodeStatus.ACTIVE)
	created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	redeemed_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
	redeemed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
	expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
	meta: Mapped[Optional[dict]] = mapped_column(sa.dialects.postgresql.JSONB, nullable=True)  # type: ignore
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


class GroupMemberInvite(Base):
	"""Invite issued to an email to join a group as a member."""
	__tablename__ = Tables.GROUP_MEMBER_INVITES

	id: Mapped[uuid.UUID] = uuid_pk()
	group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="CASCADE"))
	invited_email: Mapped[str] = mapped_column(String(EMAIL_MAX_LEN), index=True)
	invited_full_name: Mapped[Optional[str]] = mapped_column(String(FULL_NAME_MAX_LEN), nullable=True)
	status: Mapped[str] = mapped_column(String(20), default=InvitationStatus.pending.value)
	invited_by: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


class Dependent(Base):
	"""Dependent record under a group/guardian; convertible into a full user account."""
	__tablename__ = Tables.DEPENDENTS

	id: Mapped[uuid.UUID] = uuid_pk()
	group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="CASCADE"))
	guardian_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}", ondelete="CASCADE"))
	full_name: Mapped[Optional[str]] = mapped_column(String(FULL_NAME_MAX_LEN), nullable=True)
	dob: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # type: ignore
	email: Mapped[Optional[str]] = mapped_column(String(EMAIL_MAX_LEN), nullable=True)
	deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


