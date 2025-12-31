from typing import Any, Dict, List
from fastapi import APIRouter, Body, status, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, InvitationStatus, AccessLevel, Routes, Errors, Fields, Keys, Headers
from backend.schemas import CaregiverAccessUpdate, RecipientInvitationCreate
from backend.schemas.access import (
    RecipientCaregiversEnvelope,
    CaregiverRecipientsEnvelope,
    CaregiverRecipientGetResponse,
    AccessMutateEnvelope,
)
from backend.schemas.invitation import (
    InvitationCreatedEnvelope,
    CaregiverInvitesEnvelope,
    RecipientInvitesEnvelope,
    RecipientInvitationActionEnvelope,
    CaregiverInvitationActionEnvelope,
    PublicInvitationActionEnvelope,
)
from backend.routers.deps import get_current_user, get_invitations_service, get_access_service, get_group_member_invites_service
from backend.db.database import get_db
from backend.db.models import Invitation, User, RecipientCaregiverAccess
from backend.core.constants import Roles
from backend.services import InvitationsService, AccessService
import uuid
from backend.routers.http_errors import status_for_error
from backend.services.group_member_invites_service import GroupMemberInvitesService


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
public_invites_router = APIRouter(prefix=Prefix.INVITES, tags=[Tags.ACCESS])

# Dependency providers moved to deps.py (constructor-based DI)

def _err(detail: str) -> str:
    # Pass through only known error codes; default to invalid_payload
    known = {
        Errors.USER_NOT_FOUND,
        Errors.RECIPIENT_NOT_FOUND,
        Errors.INVALID_PAYLOAD,
        Errors.RECIPIENT_NOT_REGISTERED,
        Errors.CAREGIVER_NOT_REGISTERED,
        Errors.FORBIDDEN,
    }
    return detail if detail in known else Errors.INVALID_PAYLOAD



@recipient_access_router.get(Routes.ROOT, summary=Summaries.RECIPIENT_CAREGIVERS_LIST, response_model=RecipientCaregiversEnvelope)
async def list_recipient_caregivers(
    recipientId: str,
    response: Response,
    db: Session = Depends(get_db),
    access_service: AccessService = Depends(get_access_service),
) -> Dict[str, Any]:
    result = access_service.list_recipient_caregivers(db, recipient_id=recipientId)
    items = result.get(Keys.ITEMS, [])
    response.headers[Headers.TOTAL_COUNT] = str(len(items))
    return result


@recipient_access_router.post(Routes.ROOT, summary=Summaries.RECIPIENT_CAREGIVER_ASSIGN, response_model=AccessMutateEnvelope)
async def assign_caregiver(
    recipientId: str,
    payload: Dict[str, Any] = Body(default=None),
    db: Session = Depends(get_db),
    access_service: AccessService = Depends(get_access_service),
) -> Dict[str, Any]:
    caregiver_id = (payload or {}).get(Keys.CAREGIVER_ID) or (payload or {}).get("caregiverId")
    access_level = (payload or {}).get(Fields.ACCESS_LEVEL) or (payload or {}).get("access_level")
    if not caregiver_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.INVALID_PAYLOAD)
    try:
        return access_service.assign(db, recipient_id=recipientId, caregiver_id=caregiver_id, access_level=access_level)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)


@recipient_access_router.delete(Routes.CAREGIVER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.RECIPIENT_CAREGIVER_REVOKE)
async def revoke_caregiver_access(
    recipientId: str,
    caregiverId: str,
    db: Session = Depends(get_db),
    access_service: AccessService = Depends(get_access_service),
) -> None:
    access_service.revoke(db, recipient_id=recipientId, caregiver_id=caregiverId)
    return


@recipient_access_router.put(Routes.CAREGIVER_ID, summary=Summaries.RECIPIENT_CAREGIVER_UPDATE, response_model=AccessMutateEnvelope)
async def update_caregiver_access(
    recipientId: str,
    caregiverId: str,
    payload: CaregiverAccessUpdate = Body(default=None),
    db: Session = Depends(get_db),
    access_service: AccessService = Depends(get_access_service),
) -> Dict[str, Any]:
    try:
        return access_service.update(db, recipient_id=recipientId, caregiver_id=caregiverId, access_level=payload.access_level)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)

@caregiver_recipients_router.get(Routes.ROOT, summary=Summaries.CAREGIVER_RECIPIENTS_LIST, response_model=CaregiverRecipientsEnvelope)
async def list_caregiver_recipients(
    caregiverId: str,
    response: Response,
    db: Session = Depends(get_db),
    access_service: AccessService = Depends(get_access_service),
) -> Dict[str, Any]:
    result = access_service.list_caregiver_recipients(db, caregiver_id=caregiverId)
    items = result.get(Keys.ITEMS, [])
    response.headers[Headers.TOTAL_COUNT] = str(len(items))
    return result


@caregiver_recipients_router.get(Routes.RECIPIENT_ID, summary=Summaries.CAREGIVER_RECIPIENT_GET, response_model=CaregiverRecipientGetResponse)
async def get_caregiver_recipient(
    caregiverId: str, recipientId: str, db: Session = Depends(get_db), access_service: AccessService = Depends(get_access_service)
) -> Dict[str, Any]:
    try:
        return access_service.get_caregiver_recipient(db, caregiver_id=caregiverId, recipient_id=recipientId)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_err(str(e)))


@caregiver_invitations_router.post(
    Routes.ROOT,
    status_code=status.HTTP_201_CREATED,
    summary=Summaries.INVITATION_SEND,
    response_model=InvitationCreatedEnvelope,
)
async def send_invitation(
    caregiverId: str,
    payload: RecipientInvitationCreate = Body(default=None),
    db: Session = Depends(get_db),
    invitations_service: InvitationsService = Depends(get_invitations_service),
) -> Dict[str, Any]:
    try:
        data = invitations_service.send_from_caregiver(db, caregiver_id=caregiverId, email=str(payload.email))
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {Keys.MESSAGE: Messages.INVITATION_SENT, Keys.DATA: data}


@caregiver_invitations_router.get(
    Routes.ROOT, summary=Summaries.INVITATIONS_SENT_LIST, response_model=CaregiverInvitesEnvelope
)
async def list_sent_invitations(
    caregiverId: str,
    response: Response,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    invitations_service: InvitationsService = Depends(get_invitations_service),
) -> Dict[str, Any]:
    limit, offset = clamp_limit_offset(limit, offset, max_limit=100)
    try:
        result = invitations_service.list_for_caregiver(db, caregiver_id=caregiverId, limit=limit, offset=offset)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, 0))
    return {Keys.CAREGIVER_ID: caregiverId, Keys.ITEMS: result[Keys.ITEMS]}


@caregiver_invitations_router.delete(Routes.INVITATION_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.INVITATION_CANCEL)
async def cancel_invitation(caregiverId: str, invitationId: str, db: Session = Depends(get_db)) -> None:
    try:
        inv_uuid = uuid.UUID(invitationId)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.id == inv_uuid,
            Invitation.caregiver_id == caregiverId,
            Invitation.status == InvitationStatus.PENDING,
        )
    )
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    # Mark as declined (cancelled)
    invitation.status = InvitationStatus.DECLINED
    db.commit()
    return


@recipient_invitations_router.get(
    Routes.ROOT, summary=Summaries.INVITATIONS_RECEIVED_LIST, response_model=RecipientInvitesEnvelope
)
async def list_recipient_invitations(
    recipientId: str,
    response: Response,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    invitations_service: InvitationsService = Depends(get_invitations_service),
) -> Dict[str, Any]:
    limit, offset = clamp_limit_offset(limit, offset, max_limit=100)
    try:
        result = invitations_service.list_for_recipient(db, recipient_id=recipientId, limit=limit, offset=offset)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, 0))
    return {Keys.RECIPIENT_ID: recipientId, Keys.ITEMS: result[Keys.ITEMS]}


@recipient_invitations_router.post(Routes.INVITATION_ACCEPT, summary=Summaries.INVITATION_ACCEPT, response_model=RecipientInvitationActionEnvelope)
async def accept_invitation(
    recipientId: str, invitationId: str, db: Session = Depends(get_db), invitations_service: InvitationsService = Depends(get_invitations_service)
) -> Dict[str, Any]:
    try:
        return invitations_service.recipient_accept(db, recipient_id=recipientId, invitation_id=invitationId)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)


@recipient_invitations_router.post(Routes.INVITATION_DECLINE, summary=Summaries.INVITATION_DECLINE, response_model=RecipientInvitationActionEnvelope)
async def decline_invitation(
    recipientId: str, invitationId: str, db: Session = Depends(get_db), invitations_service: InvitationsService = Depends(get_invitations_service)
) -> Dict[str, Any]:
    try:
        return invitations_service.recipient_decline(db, recipient_id=recipientId, invitation_id=invitationId)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)


@recipient_invitations_router.get(Routes.INVITATION_ID, summary=Summaries.INVITATION_GET)
async def get_recipient_invitation(recipientId: str, invitationId: str) -> Dict[str, Any]:
    return {Keys.RECIPIENT_ID: recipientId, Keys.INVITATION_ID: invitationId, Keys.STATUS: InvitationStatus.PENDING}


@recipient_invitations_router.post(
    Routes.ROOT,
    status_code=status.HTTP_201_CREATED,
    summary=Summaries.INVITATION_SEND,
    response_model=InvitationCreatedEnvelope,
)
async def create_recipient_invitation(
    recipientId: str,
    payload: RecipientInvitationCreate = Body(default=None),
    db: Session = Depends(get_db),
    invitations_service: InvitationsService = Depends(get_invitations_service),
) -> Dict[str, Any]:
    try:
        data = invitations_service.send_from_recipient(db, recipient_id=recipientId, email=str(payload.email))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_err(str(e)))
    return {Keys.MESSAGE: Messages.INVITATION_SENT, Keys.DATA: data}


# Caregiver accepts or declines an invitation they received
@caregiver_invitations_router.post(Routes.INVITATION_ACCEPT, summary=Summaries.INVITATION_ACCEPT, response_model=CaregiverInvitationActionEnvelope)
async def caregiver_accept_invitation(
    caregiverId: str, invitationId: str, db: Session = Depends(get_db), invitations_service: InvitationsService = Depends(get_invitations_service)
) -> Dict[str, Any]:
    try:
        return invitations_service.caregiver_accept(db, caregiver_id=caregiverId, invitation_id=invitationId)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)


@caregiver_invitations_router.post(Routes.INVITATION_DECLINE, summary=Summaries.INVITATION_DECLINE, response_model=CaregiverInvitationActionEnvelope)
async def caregiver_decline_invitation(
    caregiverId: str, invitationId: str, db: Session = Depends(get_db), invitations_service: InvitationsService = Depends(get_invitations_service)
) -> Dict[str, Any]:
    try:
        return invitations_service.caregiver_decline(db, caregiver_id=caregiverId, invitation_id=invitationId)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)


# Recipient: list invites sent by them (to caregivers)
@recipient_invitations_router.get(Routes.SENT, summary=Summaries.INVITATIONS_SENT_LIST, response_model=RecipientInvitesEnvelope)
async def list_recipient_sent_invitations(
    recipientId: str,
    response: Response,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    invitations_service: InvitationsService = Depends(get_invitations_service),
) -> Dict[str, Any]:
    limit, offset = clamp_limit_offset(limit, offset, max_limit=100)
    try:
        result = invitations_service.list_sent_by_recipient(db, recipient_id=recipientId, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_err(str(e)))
    response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, 0))
    return {Keys.RECIPIENT_ID: recipientId, Keys.ITEMS: result[Keys.ITEMS]}


# Accept by signed token (no auth required)
@public_invites_router.post(Routes.ACCEPT_BY_TOKEN, summary=Summaries.INVITATION_ACCEPT, response_model=PublicInvitationActionEnvelope)
async def accept_by_token(
    payload: Dict[str, Any] = Body(default=None),
    db: Session = Depends(get_db),
    invitations_service: InvitationsService = Depends(get_invitations_service),
) -> Dict[str, Any]:
    token = (payload or {}).get(Keys.TOKEN)
    try:
        return invitations_service.accept_by_token(db, token=token)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)

# Group member invite accept-by-token (public)
@public_invites_router.post("/group-member/accept-by-token", summary=Summaries.INVITATION_ACCEPT)
async def accept_group_member_by_token(
    payload: Dict[str, Any] = Body(default=None),
    db: Session = Depends(get_db),
    svc: GroupMemberInvitesService = Depends(get_group_member_invites_service),
) -> Dict[str, Any]:
    token = (payload or {}).get(Keys.TOKEN)
    try:
        return svc.accept_by_token(db, token=token)
    except ValueError as e:
        detail = _err(str(e))
        raise HTTPException(status_code=status_for_error(detail), detail=detail)

