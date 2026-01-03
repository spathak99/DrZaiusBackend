from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base, uuid_pk, ts_created, ts_updated, FILE_NAME_MAX_LEN, DOWNLOAD_LINK_MAX_LEN, ACCESS_LEVEL_MAX_LEN
from backend.core.constants import Tables, Fields


class File(Base):
	"""A file uploaded on behalf of a recipient."""
	__tablename__ = Tables.FILES

	id: Mapped[uuid.UUID] = uuid_pk()
	recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	file_name: Mapped[Optional[str]] = mapped_column(String(FILE_NAME_MAX_LEN), nullable=True)
	download_link: Mapped[Optional[str]] = mapped_column(String(DOWNLOAD_LINK_MAX_LEN), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


class FileAccess(Base):
	"""Access control edge granting a caregiver access to a file."""
	__tablename__ = Tables.FILE_ACCESS

	id: Mapped[uuid.UUID] = uuid_pk()
	file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.FILES}.{Fields.ID}"))
	caregiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{Tables.USERS}.{Fields.ID}"))
	access_level: Mapped[Optional[str]] = mapped_column(String(ACCESS_LEVEL_MAX_LEN), nullable=True)
	created_at: Mapped[datetime] = ts_created()
	updated_at: Mapped[datetime] = ts_updated()


