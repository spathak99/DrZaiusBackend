from typing import Any, Dict, List
from fastapi import APIRouter, Body, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, InvitationStatus, AccessLevel, Routes, Errors, Fields, Keys
from backend.services import AccessService
from backend.schemas import CaregiverAccessUpdate, RecipientInvitationCreate
from backend.routers.deps import get_current_user
from backend.db.database import get_db
from backend.db.models import Invitation, User, RecipientCaregiverAccess
import uuid


recipient_access_router = APIRouter(
    prefix=Prefix.RECIPIENT_ACCESS, tags=[Tags.ACCESS], dependencies=[Depends(get_current_user)]
)
caregiver_recipients_router = APIRouter(
    prefix=Prefix.CAREGIVER_RECIPIENTS, tags=[Tags.RELATIONS], dependencies=[Depends(get_current_user)]
)
caregiver_invitations_router = APIRouter(
    prefix=Prefix.CAREGIVER_INVITATIONS, tags=[Tags.ACCESS], dependencies=[Depends(get_current_user)]
)
recipient_invitations_router = APIRouter(
    prefix=Prefix.RECIPIENT_INVITATIONS, tags=[Tags.ACCESS], dependencies=[Depends(get_current_user)]
)

service = AccessService()


@recipient_access_router.get(Routes.ROOT, summary=Summaries.RECIPIENT_CAREGIVERS_LIST)
async def list_recipient_caregivers(recipientId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    rows = db.scalars(
        select(RecipientCaregiverAccess).where(RecipientCaregiverAccess.recipient_id == recipientId)
    ).all()
    items: List[Dict[str, Any]] = [
        {Keys.CAREGIVER_ID: r.caregiver_id, Fields.ACCESS_LEVEL: r.access_level} for r in rows
    ]
    return {Keys.RECIPIENT_ID: recipientId, Keys.ITEMS: items}


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
async def list_caregiver_recipients(caregiverId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    rows = db.scalars(
        select(RecipientCaregiverAccess).where(RecipientCaregiverAccess.caregiver_id == caregiverId)
    ).all()
    items: List[Dict[str, Any]] = [
        {Keys.RECIPIENT_ID: r.recipient_id, Fields.ACCESS_LEVEL: r.access_level} for r in rows
    ]
    return {Keys.CAREGIVER_ID: caregiverId, Keys.ITEMS: items}


@caregiver_recipients_router.get(Routes.RECIPIENT_ID, summary=Summaries.CAREGIVER_RECIPIENT_GET)
async def get_caregiver_recipient(caregiverId: str, recipientId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    rel = db.scalar(
        select(RecipientCaregiverAccess).where(
            RecipientCaregiverAccess.caregiver_id == caregiverId,
            RecipientCaregiverAccess.recipient_id == recipientId,
        )
    )
    if rel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    return {Keys.CAREGIVER_ID: caregiverId, Keys.RECIPIENT_ID: recipientId, Fields.ACCESS_LEVEL: rel.access_level}


@caregiver_invitations_router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.INVITATION_SEND)
async def send_invitation(caregiverId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.INVITATION_SENT, Keys.CAREGIVER_ID: caregiverId, Keys.DATA: payload}


@caregiver_invitations_router.get(Routes.ROOT, summary=Summaries.INVITATIONS_SENT_LIST)
async def list_sent_invitations(caregiverId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    invites = db.scalars(
        select(Invitation).where(Invitation.caregiver_id == caregiverId, Invitation.status == InvitationStatus.PENDING)
    ).all()
    items: List[Dict[str, Any]] = [
        {
            Fields.ID: inv.id,
            Keys.CAREGIVER_ID: inv.caregiver_id,
            Keys.RECIPIENT_ID: inv.recipient_id,
            Keys.STATUS: inv.status,
        }
        for inv in invites
    ]
    return {Keys.CAREGIVER_ID: caregiverId, Keys.ITEMS: items}


@caregiver_invitations_router.delete(Routes.INVITATION_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.INVITATION_CANCEL)
async def cancel_invitation(caregiverId: str, invitationId: str) -> None:
    return


@recipient_invitations_router.get(Routes.ROOT, summary=Summaries.INVITATIONS_RECEIVED_LIST)
async def list_recipient_invitations(recipientId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Validate recipient
    recipient = db.scalar(select(User).where(User.id == recipientId))
    if recipient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    invs = db.scalars(
        select(Invitation).where(
            Invitation.recipient_id == recipientId,
            Invitation.status == InvitationStatus.PENDING,
        )
    ).all()
    items: List[Dict[str, Any]] = [
        {
            Fields.ID: i.id,
            Keys.CAREGIVER_ID: i.caregiver_id,
            Keys.RECIPIENT_ID: i.recipient_id,
            Keys.STATUS: i.status,
        }
        for i in invs
    ]
    return {Keys.RECIPIENT_ID: recipientId, Keys.ITEMS: items}


@recipient_invitations_router.post(Routes.INVITATION_ACCEPT, summary=Summaries.INVITATION_ACCEPT)
async def accept_invitation(recipientId: str, invitationId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        inv_uuid = uuid.UUID(invitationId)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.id == inv_uuid, Invitation.recipient_id == recipientId, Invitation.status == InvitationStatus.PENDING
        )
    )
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    # Mark accepted
    invitation.status = InvitationStatus.ACCEPTED
    # Grant default READ access entry
    access = RecipientCaregiverAccess(recipient_id=invitation.recipient_id, caregiver_id=invitation.caregiver_id)
    db.add(access)
    db.commit()
    db.refresh(invitation)
    return {Keys.MESSAGE: Messages.INVITATION_ACCEPTED, Keys.RECIPIENT_ID: recipientId, Keys.INVITATION_ID: invitationId}


@recipient_invitations_router.post(Routes.INVITATION_DECLINE, summary=Summaries.INVITATION_DECLINE)
async def decline_invitation(recipientId: str, invitationId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        inv_uuid = uuid.UUID(invitationId)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.id == inv_uuid, Invitation.recipient_id == recipientId, Invitation.status == InvitationStatus.PENDING
        )
    )
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    invitation.status = InvitationStatus.DECLINED
    db.commit()
    return {Keys.MESSAGE: Messages.INVITATION_DECLINED, Keys.RECIPIENT_ID: recipientId, Keys.INVITATION_ID: invitationId}


@recipient_invitations_router.get(Routes.INVITATION_ID, summary=Summaries.INVITATION_GET)
async def get_recipient_invitation(recipientId: str, invitationId: str) -> Dict[str, Any]:
    return {Keys.RECIPIENT_ID: recipientId, Keys.INVITATION_ID: invitationId, Keys.STATUS: InvitationStatus.PENDING}


@recipient_invitations_router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.INVITATION_SEND)
async def create_recipient_invitation(
    recipientId: str,
    payload: RecipientInvitationCreate = Body(default=None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    # Validate recipient
    recipient = db.scalar(select(User).where(User.id == recipientId))
    if recipient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    # Resolve caregiver by email
    caregiver = db.scalar(select(User).where(User.email == payload.email))
    if caregiver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    inv = Invitation(caregiver_id=caregiver.id, recipient_id=recipient.id, status=InvitationStatus.PENDING)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return {
        Keys.MESSAGE: Messages.INVITATION_SENT,
        Keys.DATA: {
            Fields.ID: inv.id,
            Keys.CAREGIVER_ID: inv.caregiver_id,
            Keys.RECIPIENT_ID: inv.recipient_id,
            Keys.STATUS: inv.status,
        },
    }


