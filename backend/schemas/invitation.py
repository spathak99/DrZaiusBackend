from uuid import UUID
from pydantic import BaseModel, EmailStr
from backend.schemas.common import Timestamped, InvitationStatus, AccessLevel


class InvitationCreate(BaseModel):
    caregiver_id: UUID
    recipient_id: UUID


class InvitationResponse(Timestamped):
    id: UUID
    caregiver_id: UUID
    recipient_id: UUID
    status: InvitationStatus


class RecipientInvitationCreate(BaseModel):
    email: EmailStr
    role: AccessLevel
    