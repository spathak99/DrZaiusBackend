from uuid import UUID
from pydantic import BaseModel, EmailStr
from backend.schemas.common import Timestamped, InvitationStatus, AccessLevel
from typing import Optional, List


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


# Response models (use wire-format field names)
class SenderInfo(BaseModel):
    sender_id: Optional[str] = None
    sender_email: Optional[str] = None
    sender_full_name: Optional[str] = None


class InvitationListItem(SenderInfo):
    id: str
    caregiverId: Optional[str] = None
    recipientId: Optional[str] = None
    status: InvitationStatus
    sent_by: str


class InvitationCreatedData(SenderInfo):
    id: str
    caregiverId: Optional[str] = None
    recipientId: Optional[str] = None
    status: InvitationStatus
    sent_by: str
    acceptUrl: Optional[str] = None


class InvitationCreatedEnvelope(BaseModel):
    message: str
    data: InvitationCreatedData


class CaregiverInvitesEnvelope(BaseModel):
    caregiverId: str
    items: List[InvitationListItem]


class RecipientInvitesEnvelope(BaseModel):
    recipientId: str
    items: List[InvitationListItem]


# Action responses for accept/decline flows
class RecipientInvitationActionEnvelope(BaseModel):
    message: str
    recipientId: str
    invitationId: str


class CaregiverInvitationActionEnvelope(BaseModel):
    message: str
    caregiverId: str
    invitationId: str


class PublicInvitationActionEnvelope(BaseModel):
    message: str
    invitationId: str