from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages, InvitationStatus, AccessLevel, Routes
from backend.services import AccessService
from backend.schemas import CaregiverAccessUpdate


recipient_access_router = APIRouter(prefix=Prefix.RECIPIENT_ACCESS, tags=[Tags.ACCESS])
caregiver_recipients_router = APIRouter(prefix=Prefix.CAREGIVER_RECIPIENTS, tags=[Tags.RELATIONS])
caregiver_invitations_router = APIRouter(prefix=Prefix.CAREGIVER_INVITATIONS, tags=[Tags.ACCESS])
recipient_invitations_router = APIRouter(prefix=Prefix.RECIPIENT_INVITATIONS, tags=[Tags.ACCESS])

service = AccessService()


@recipient_access_router.get(Routes.ROOT, summary=Summaries.RECIPIENT_CAREGIVERS_LIST)
async def list_recipient_caregivers(recipientId: str) -> Dict[str, Any]:
    return {"recipientId": recipientId, "items": service.list_recipient_caregivers(recipientId)}


@recipient_access_router.post(Routes.ROOT, summary=Summaries.RECIPIENT_CAREGIVER_ASSIGN)
async def assign_caregiver(recipientId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return service.assign_caregiver(recipientId, payload)


@recipient_access_router.delete(Routes.CAREGIVER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.RECIPIENT_CAREGIVER_REVOKE)
async def revoke_caregiver_access(recipientId: str, caregiverId: str) -> None:
    service.revoke_caregiver(recipientId, caregiverId)
    return


@recipient_access_router.put(Routes.CAREGIVER_ID, summary=Summaries.RECIPIENT_CAREGIVER_UPDATE)
async def update_caregiver_access(
    recipientId: str, caregiverId: str, payload: CaregiverAccessUpdate = Body(default=None)
) -> Dict[str, Any]:
    return service.update_caregiver_access(recipientId, caregiverId, payload.model_dump())


@caregiver_recipients_router.get(Routes.ROOT, summary=Summaries.CAREGIVER_RECIPIENTS_LIST)
async def list_caregiver_recipients(caregiverId: str) -> Dict[str, Any]:
    return {"caregiverId": caregiverId, "items": service.list_caregiver_recipients(caregiverId)}


@caregiver_recipients_router.get(Routes.RECIPIENT_ID, summary=Summaries.CAREGIVER_RECIPIENT_GET)
async def get_caregiver_recipient(caregiverId: str, recipientId: str) -> Dict[str, Any]:
    rel = service.get_caregiver_recipient(caregiverId, recipientId)
    if "access_level" not in rel:
        rel["access_level"] = AccessLevel.READ
    return rel


@caregiver_invitations_router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.INVITATION_SEND)
async def send_invitation(caregiverId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.INVITATION_SENT, "caregiverId": caregiverId, "data": payload}


@caregiver_invitations_router.get(Routes.ROOT, summary=Summaries.INVITATIONS_SENT_LIST)
async def list_sent_invitations(caregiverId: str) -> Dict[str, Any]:
    return {"caregiverId": caregiverId, "items": []}


@caregiver_invitations_router.delete(Routes.INVITATION_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.INVITATION_CANCEL)
async def cancel_invitation(caregiverId: str, invitationId: str) -> None:
    return


@recipient_invitations_router.get(Routes.ROOT, summary=Summaries.INVITATIONS_RECEIVED_LIST)
async def list_recipient_invitations(recipientId: str) -> Dict[str, Any]:
    return {"recipientId": recipientId, "items": []}


@recipient_invitations_router.post(Routes.INVITATION_ACCEPT, summary=Summaries.INVITATION_ACCEPT)
async def accept_invitation(recipientId: str, invitationId: str) -> Dict[str, Any]:
    return {"message": Messages.INVITATION_ACCEPTED, "recipientId": recipientId, "invitationId": invitationId}


@recipient_invitations_router.post(Routes.INVITATION_DECLINE, summary=Summaries.INVITATION_DECLINE)
async def decline_invitation(recipientId: str, invitationId: str) -> Dict[str, Any]:
    return {"message": Messages.INVITATION_DECLINED, "recipientId": recipientId, "invitationId": invitationId}


@recipient_invitations_router.get(Routes.INVITATION_ID, summary=Summaries.INVITATION_GET)
async def get_recipient_invitation(recipientId: str, invitationId: str) -> Dict[str, Any]:
    return {"recipientId": recipientId, "invitationId": invitationId, "status": InvitationStatus.PENDING}


