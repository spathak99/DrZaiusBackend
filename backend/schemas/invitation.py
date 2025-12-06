from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import Timestamped, InvitationStatus


class InvitationCreate(BaseModel):
    caregiver_id: UUID
    recipient_id: UUID


class InvitationResponse(Timestamped):
    id: UUID
    caregiver_id: UUID
    recipient_id: UUID
    status: InvitationStatus

