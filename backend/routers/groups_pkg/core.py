from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.constants import Routes, Keys, Fields, Errors, Summaries, Headers, GroupRoles, Messages, Roles, Pagination as PaginationConsts
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_groups_service, get_memberships_service
from backend.db.models import User
from backend.utils.pagination import clamp_limit_offset
from backend.routers.http_errors import status_for_error
from backend.services.auth_service import hash_password
from backend.schemas.groups import (
	GroupCreate,
	GroupUpdate,
	GroupsListEnvelope,
	GroupDetailEnvelope,
	MembershipsListEnvelope,
	ActionEnvelope,
	GroupListItem,
	GroupDetail,
	MembershipItem,
)
from backend.services.groups_service import GroupsService, MembershipsService
from datetime import date
import secrets

router = APIRouter()


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.GROUP_CREATE, response_model=GroupDetailEnvelope)
async def create_group(payload: GroupCreate = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
	if (getattr(current_user, "account_type", None) or "").lower() != "group":
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
	data = svc.create(db, name=payload.name, description=payload.description, created_by=str(current_user.id))
	return {Keys.DATA: GroupDetail(**{
		Fields.ID: data.get(Fields.ID),
		Fields.NAME: data.get(Fields.NAME),
		Fields.DESCRIPTION: data.get(Fields.DESCRIPTION),
		Fields.CREATED_BY: data.get(Fields.CREATED_BY),
		Fields.CREATED_AT: data.get(Fields.CREATED_AT),
	})}


@router.get(Routes.ROOT, summary=Summaries.GROUPS_LIST, response_model=GroupsListEnvelope)
async def list_my_groups(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
	rows = svc.list_mine(db, user_id=str(current_user.id))
	items = [GroupListItem(id=r["id"], name=r["name"], description=r.get("description")) for r in rows]
	response.headers[Headers.TOTAL_COUNT] = str(len(items))
	return {Keys.ITEMS: items}


@router.get(Routes.ID, summary=Summaries.GROUP_GET, response_model=GroupDetailEnvelope)
async def get_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
	try:
		data = svc.get(db, group_id=id, user_id=str(current_user.id))
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {Keys.DATA: GroupDetail(**{
		Fields.ID: data.get(Fields.ID),
		Fields.NAME: data.get(Fields.NAME),
		Fields.DESCRIPTION: data.get(Fields.DESCRIPTION),
		Fields.CREATED_BY: data.get(Fields.CREATED_BY),
		Fields.CREATED_AT: data.get(Fields.CREATED_AT),
	})}


@router.put(Routes.ID, summary=Summaries.GROUP_UPDATE, response_model=GroupDetailEnvelope)
async def update_group(id: str, payload: GroupUpdate = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
	try:
		data = svc.update(db, group_id=id, user_id=str(current_user.id), name=payload.name, description=payload.description)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {Keys.DATA: GroupDetail(**{
		Fields.ID: data.get(Fields.ID),
		Fields.NAME: data.get(Fields.NAME),
		Fields.DESCRIPTION: data.get(Fields.DESCRIPTION),
		Fields.CREATED_BY: data.get(Fields.CREATED_BY),
		Fields.CREATED_AT: data.get(Fields.CREATED_AT),
	})}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_DELETE)
async def delete_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> None:
	try:
		svc.delete(db, group_id=id, user_id=str(current_user.id))
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return


@router.get(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBERS_LIST, response_model=MembershipsListEnvelope)
async def list_members(id: str, response: Response, limit: int = PaginationConsts.DEFAULT_LIMIT, offset: int = PaginationConsts.DEFAULT_OFFSET, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> Dict[str, Any]:
	limit, offset = clamp_limit_offset(limit, offset, max_limit=PaginationConsts.MAX_LIMIT)
	try:
		result = svc.list_by_group(db, group_id=id, actor_id=str(current_user.id), limit=limit, offset=offset)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	raw_items = result[Keys.ITEMS]
	user_ids = [r.get("user_id") or r.get("userId") or r[Keys.USER_ID] for r in raw_items]
	users_map = {str(u.id): u for u in db.scalars(select(User).where(User.id.in_(user_ids))).all()}
	items = []
	for r in raw_items:
		uid = r.get("user_id") if "user_id" in r else (r.get("userId") or r[Keys.USER_ID])
		u = users_map.get(str(uid))
		items.append(MembershipItem(id=r["id"], userId=str(uid), role=r["role"], full_name=(u.full_name if u else None), email=(u.email if u else None), age=(u.age if u else None)))
	response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
	return {Keys.ITEMS: items}


@router.post(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBER_ADD, response_model=ActionEnvelope)
async def add_member(id: str, request: Request, payload: "MemberAdd" = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> Dict[str, Any]:
	from pydantic import BaseModel
	class MemberAdd(BaseModel):
		email: str
		role: Optional[str] = None
		dob: Optional[str] = None
		first_name: Optional[str] = None
		last_name: Optional[str] = None
		age: Optional[int] = None
	try:
		normalized = (payload.email or "").strip().lower()
		temp_password: Optional[str] = None
		target = db.scalar(select(User).where(User.email == normalized))
		if target is None:
			age_val: Optional[int] = None
			if payload.dob:
				try:
					dob_dt = date.fromisoformat(payload.dob)
					today = date.today()
					age_val = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
				except Exception:
					pass
			if payload.age is not None and isinstance(payload.age, int):
				age_val = payload.age
			full_name: Optional[str] = None
			if payload.first_name or payload.last_name:
				full_name = f"{(payload.first_name or '').strip()} {(payload.last_name or '').strip()}".strip() or None
			temp_password = secrets.token_urlsafe(12)
			target = User(username=normalized, email=normalized, password_hash=hash_password(temp_password), role=Roles.CAREGIVER, full_name=full_name, age=age_val, corpus_uri=f"user://{normalized}/corpus", chat_history_uri=None)
			db.add(target)
			db.commit()
			db.refresh(target)
		svc.add(db, group_id=id, actor_id=str(current_user.id), user_id=str(target.id), role=payload.role or GroupRoles.MEMBER)
		if temp_password:
			import logging
			logging.getLogger(__name__).info("auto_user_created", extra={"email": normalized, "tempPassword": temp_password, "groupId": id})
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {Keys.MESSAGE: Messages.GROUP_MEMBER_ADDED}


@router.put(Routes.ID + Routes.ACCESS + Routes.USER_ID + Routes.ROLE, summary=Summaries.GROUP_MEMBER_UPDATE, response_model=ActionEnvelope)
async def change_role(id: str, userId: str, request: Request, payload: "MemberRoleUpdate" = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> Dict[str, Any]:
	from pydantic import BaseModel
	class MemberRoleUpdate(BaseModel):
		role: str
	try:
		svc.change_role(db, group_id=id, actor_id=str(current_user.id), user_id=userId, role=payload.role)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {Keys.MESSAGE: Messages.GROUP_MEMBER_ROLE_UPDATED}


@router.delete(Routes.ID + Routes.ACCESS + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_MEMBER_REMOVE)
async def remove_member(id: str, userId: str, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
	try:
		svc.remove(db, group_id=id, actor_id=str(current_user.id), user_id=userId)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return


@router.post(Routes.ID + Routes.ACCESS + Routes.SELF, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_LEAVE)
async def leave_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
	try:
		svc.leave(db, group_id=id, user_id=str(current_user.id))
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return


