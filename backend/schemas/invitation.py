from uuid import UUID
from pydantic import BaseModel


class InvitationCreate(BaseModel):
    caregiver_id: UUID
    recipient_id: UUID


