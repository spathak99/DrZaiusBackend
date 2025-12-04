from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class FileUpload(BaseModel):
    recipient_id: Optional[UUID] = None
    file_name: Optional[str] = None


class FileAccessGrant(BaseModel):
    caregiver_id: UUID
    access_level: str


class FileAccessUpdate(BaseModel):
    access_level: str


