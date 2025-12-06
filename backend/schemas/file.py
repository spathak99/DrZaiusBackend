from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import Timestamped, AccessLevel


class FileUpload(BaseModel):
    recipient_id: Optional[UUID] = None
    file_name: Optional[str] = None


class FileAccessGrant(BaseModel):
    caregiver_id: UUID
    access_level: AccessLevel


class FileAccessUpdate(BaseModel):
    access_level: AccessLevel


class FileResponse(Timestamped):
    id: UUID
    recipient_id: UUID
    file_name: Optional[str] = None
    download_link: Optional[str] = None


class FileAccessEntry(Timestamped):
    id: UUID
    file_id: UUID
    caregiver_id: UUID
    access_level: Optional[AccessLevel] = None


