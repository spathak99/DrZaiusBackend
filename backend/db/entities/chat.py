from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base, uuid_pk, ts_created, ts_updated, CHAT_NAME_MAX_LEN
from backend.core.constants import Tables, Fields
from .user import User


class Chat(Base):
	"""Chat entity containing participants and messages."""
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
	"""Membership edge between a user and a chat."""
	__tablename__ = Tables.CHAT_PARTICIPANTS

	id: Mapped[uuid.UUID] = uuid_pk()
	chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.CHATS}.{Fields.ID}"))
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()

	chat: Mapped[Chat] = relationship(back_populates="participants")
	user: Mapped[User] = relationship()


class Message(Base):
	"""Message posted in a chat by an optional sender."""
	__tablename__ = Tables.MESSAGES

	id: Mapped[uuid.UUID] = uuid_pk()
	chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.CHATS}.{Fields.ID}"))
	sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"), nullable=True)
	content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()

	chat: Mapped[Chat] = relationship(back_populates="messages")
	sender: Mapped[Optional[User]] = relationship()


