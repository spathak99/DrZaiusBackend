from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import AccessLevel, Timestamped


class CaregiverAccessUpdate(BaseModel):
    access_level: AccessLevel


class CaregiverAssign(BaseModel):
    caregiver_id: UUID
    access_level: AccessLevel | None = None


class CaregiverAccessResponse(Timestamped):
    id: UUID
    recipient_id: UUID
    caregiver_id: UUID
    access_level: AccessLevel | None = None


