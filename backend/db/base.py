"""SQLAlchemy base and shared model utilities/constants."""
from __future__ import annotations

import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
	"""Base declarative class for all models."""
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


