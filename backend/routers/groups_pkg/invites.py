from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from backend.core.constants import Routes, Keys, Fields, Summaries, Headers, Messages, Pagination as PaginationConsts
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_group_member_invites_service
from backend.routers.http_errors import status_for_error
from backend.schemas.group_invites import GroupMemberInviteCreate, GroupMemberInviteItem, GroupMemberInvitesEnvelope, GroupMemberInviteCreatedEnvelope
from backend.services.group_member_invites_service import GroupMemberInvitesService
from backend.utils.pagination import clamp_limit_offset

router = APIRouter()


@router.post(Routes.ID + Routes.ACCESS + "/invitations", summary="Send group member invite", response_model=GroupMemberInviteCreatedEnvelope)
async def send_group_member_invite(id: str, request: Request, payload: GroupMemberInviteCreate = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupMemberInvitesService = Depends(get_group_member_invites_service)) -> Dict[str, Any]:
	try:
		data = svc.send(db, group_id=id, actor_id=str(current_user.id), email=str(payload.email), full_name=payload.full_name)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {Keys.MESSAGE: Messages.INVITATION_SENT, Keys.DATA: GroupMemberInviteItem(**{"id": data.get(Fields.ID), "invited_email": data.get(Keys.INVITED_EMAIL), "invited_full_name": data.get(Keys.INVITED_FULL_NAME), "status": data.get(Keys.STATUS), Keys.ACCEPT_URL: data.get(Keys.ACCEPT_URL)})}


@router.get(Routes.ID + Routes.ACCESS + "/invitations", summary="List pending group member invites", response_model=GroupMemberInvitesEnvelope)
async def list_group_member_invites(id: str, response: Response, limit: int = PaginationConsts.DEFAULT_LIMIT, offset: int = PaginationConsts.DEFAULT_OFFSET, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupMemberInvitesService = Depends(get_group_member_invites_service)) -> Dict[str, Any]:
	limit, offset = clamp_limit_offset(limit, offset, max_limit=PaginationConsts.MAX_LIMIT)
	try:
		result = svc.list_pending(db, group_id=id, limit=limit, offset=offset)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	items = [GroupMemberInviteItem(**it) for it in result.get(Keys.ITEMS, [])]
	response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
	return {Keys.ITEMS: items}


