from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class Role(str, Enum):
    recipient = "recipient"
    caregiver = "caregiver"


class InvitationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class AccessLevel(str, Enum):
    read = "read"
    write = "write"
    admin = "admin"

class StorageProvider(str, Enum):
    gcs = "gcs"
    s3 = "s3"
    azure = "azure"
    local = "local"


class Timestamped(BaseModel):
    created_at: datetime
    updated_at: datetime


