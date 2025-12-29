import uuid
import sqlalchemy as sa
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from backend.schemas.common import InvitationStatus
from backend.core.constants import Tables, Fields, Keys, PaymentCodeStatus


class Base(DeclarativeBase):
    pass


# String length constants
USERNAME_MAX_LEN = 255
EMAIL_MAX_LEN = 255
PASSWORD_HASH_MAX_LEN = 255
ROLE_MAX_LEN = 20
ACCESS_LEVEL_MAX_LEN = 20
CHAT_NAME_MAX_LEN = 255
FILE_NAME_MAX_LEN = 255
DOWNLOAD_LINK_MAX_LEN = 255
INVITATION_STATUS_MAX_LEN = 20
CORPUS_URI_MAX_LEN = 2048
CHAT_HISTORY_URI_MAX_LEN = 2048
PROJECT_ID_MAX_LEN = 128
BUCKET_NAME_MAX_LEN = 1024
GROUP_NAME_MAX_LEN = 255
GROUP_DESC_MAX_LEN = 1024
GROUP_ROLE_MAX_LEN = 20
FULL_NAME_MAX_LEN = 255
PHONE_NUMBER_MAX_LEN = 32
COUNTRY_MAX_LEN = 64
AVATAR_URI_MAX_LEN = 2048


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def ts_created() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


def ts_updated() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = Tables.USERS

    id: Mapped[uuid.UUID] = uuid_pk()
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LEN), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LEN), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LEN), nullable=False)
    role: Mapped[str] = mapped_column(String(ROLE_MAX_LEN), nullable=False)
    corpus_uri: Mapped[str] = mapped_column(String(CORPUS_URI_MAX_LEN), nullable=False)
    chat_history_uri: Mapped[str] = mapped_column(String(CHAT_HISTORY_URI_MAX_LEN), nullable=True)
    account_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="SET NULL"), nullable=True)
    gcp_project_id: Mapped[Optional[str]] = mapped_column(String(PROJECT_ID_MAX_LEN), nullable=True)
    temp_bucket: Mapped[Optional[str]] = mapped_column(String(BUCKET_NAME_MAX_LEN), nullable=True)
    payment_info: Mapped[Optional[dict]] = mapped_column(sa.dialects.postgresql.JSONB, nullable=True)
    # Profile fields (for mobile UX)
    full_name: Mapped[Optional[str]] = mapped_column(String(FULL_NAME_MAX_LEN), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(PHONE_NUMBER_MAX_LEN), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(COUNTRY_MAX_LEN), nullable=True)
    avatar_uri: Mapped[Optional[str]] = mapped_column(String(AVATAR_URI_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    chats_created: Mapped[List["Chat"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    groups_memberships: Mapped[List["GroupMembership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # Optional read-only convenience to directly access groups
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary=Tables.GROUP_MEMBERSHIPS,
        primaryjoin="User.id==GroupMembership.user_id",
        secondaryjoin="Group.id==GroupMembership.group_id",
        viewonly=True,
    )


class RecipientCaregiverAccess(Base):
    __tablename__ = Tables.RECIPIENT_CAREGIVER_ACCESS

    id: Mapped[uuid.UUID] = uuid_pk()
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
    caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
    access_level: Mapped[Optional[str]] = mapped_column(String(ACCESS_LEVEL_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


class Chat(Base):
    __tablename__ = Tables.CHATS

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[Optional[str]] = mapped_column(String(CHAT_NAME_MAX_LEN), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    creator: Mapped[Optional[User]] = relationship(back_populates="chats_created")
    participants: Mapped[List["ChatParticipant"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    messages: Mapped[List["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")


class ChatParticipant(Base):
    __tablename__ = Tables.CHAT_PARTICIPANTS

    id: Mapped[uuid.UUID] = uuid_pk()
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.CHATS}.{Fields.ID}"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    chat: Mapped[Chat] = relationship(back_populates="participants")
    user: Mapped[User] = relationship()


class Message(Base):
    __tablename__ = Tables.MESSAGES

    id: Mapped[uuid.UUID] = uuid_pk()
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.CHATS}.{Fields.ID}"))
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    chat: Mapped[Chat] = relationship(back_populates="messages")
    sender: Mapped[Optional[User]] = relationship()


class Invitation(Base):
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


class File(Base):
    __tablename__ = Tables.FILES

    id: Mapped[uuid.UUID] = uuid_pk()
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
    file_name: Mapped[Optional[str]] = mapped_column(String(FILE_NAME_MAX_LEN), nullable=True)
    download_link: Mapped[Optional[str]] = mapped_column(String(DOWNLOAD_LINK_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


class FileAccess(Base):
    __tablename__ = Tables.FILE_ACCESS

    id: Mapped[uuid.UUID] = uuid_pk()
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.FILES}.{Fields.ID}"))
    caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
    access_level: Mapped[Optional[str]] = mapped_column(String(ACCESS_LEVEL_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


class Group(Base):
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
    __tablename__ = Tables.GROUP_PAYMENT_CODES

    id: Mapped[uuid.UUID] = uuid_pk()
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.GROUPS}.{Fields.ID}", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default=PaymentCodeStatus.ACTIVE)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
    redeemed_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(sa.dialects.postgresql.JSONB, nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

