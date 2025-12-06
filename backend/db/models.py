import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from backend.schemas.common import InvitationStatus


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
FILE_URL_MAX_LEN = 255


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def ts_created() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


def ts_updated() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LEN), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LEN), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LEN), nullable=False)
    role: Mapped[str] = mapped_column(String(ROLE_MAX_LEN), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(FILE_URL_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    chats_created: Mapped[List["Chat"]] = relationship(back_populates="creator", cascade="all, delete-orphan")


class RecipientCaregiverAccess(Base):
    __tablename__ = "recipient_caregiver_access"

    id: Mapped[uuid.UUID] = uuid_pk()
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    access_level: Mapped[Optional[str]] = mapped_column(String(ACCESS_LEVEL_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[Optional[str]] = mapped_column(String(CHAT_NAME_MAX_LEN), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    creator: Mapped[Optional[User]] = relationship(back_populates="chats_created")
    participants: Mapped[List["ChatParticipant"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    messages: Mapped[List["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id: Mapped[uuid.UUID] = uuid_pk()
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    chat: Mapped[Chat] = relationship(back_populates="participants")
    user: Mapped[User] = relationship()


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = uuid_pk()
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()

    chat: Mapped[Chat] = relationship(back_populates="messages")
    sender: Mapped[Optional[User]] = relationship()


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = uuid_pk()
    caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(INVITATION_STATUS_MAX_LEN), default=InvitationStatus.pending.value)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = uuid_pk()
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    file_name: Mapped[Optional[str]] = mapped_column(String(FILE_NAME_MAX_LEN), nullable=True)
    download_link: Mapped[Optional[str]] = mapped_column(String(DOWNLOAD_LINK_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


class FileAccess(Base):
    __tablename__ = "file_access"

    id: Mapped[uuid.UUID] = uuid_pk()
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files.id"))
    caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    access_level: Mapped[Optional[str]] = mapped_column(String(ACCESS_LEVEL_MAX_LEN), nullable=True)
    created_at: Mapped[datetime] = ts_created()
    updated_at: Mapped[datetime] = ts_updated()


