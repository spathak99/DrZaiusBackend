from typing import Any, Dict, List, Optional
import logging
from datetime import date
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, Routes, GroupRoles, Messages, Headers, Roles, Pagination as PaginationConsts
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_groups_service, get_memberships_service, get_group_member_invites_service, get_dependents_service
from backend.db.models import User
import secrets
from backend.services.groups_service import GroupsService, MembershipsService
from backend.services.group_member_invites_service import GroupMemberInvitesService
from backend.services.dependents_service import DependentsService
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
from backend.schemas.group_invites import (
    GroupMemberInviteCreate,
    GroupMemberInviteItem,
    GroupMemberInvitesEnvelope,
    GroupMemberInviteCreatedEnvelope,
)
from backend.schemas.dependents import (
    DependentCreate,
    DependentItem,
    DependentsEnvelope,
    DependentConvertRequest,
    DependentConvertResponse,
)
from backend.rate_limit import rl_mutation

router = APIRouter(prefix=Prefix.GROUPS, tags=[Tags.GROUPS], dependencies=[Depends(get_current_user)])


class MemberAdd(BaseModel):
    email: str
    role: Optional[str] = None
    dob: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None


class MemberRoleUpdate(BaseModel):
    role: str


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.GROUP_CREATE, response_model=GroupDetailEnvelope)
async def create_group(
    payload: GroupCreate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: GroupsService = Depends(get_groups_service),
) -> Dict[str, Any]:
    # Only group-plan accounts can create/manage groups
    if (getattr(current_user, "account_type", None) or "").lower() != "group":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    data = svc.create(db, name=payload.name, description=payload.description, created_by=str(current_user.id))
    return {Keys.DATA: GroupDetail(**{
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_at": data.get("created_at"),
    })}


@router.get(Routes.ROOT, summary=Summaries.GROUPS_LIST, response_model=GroupsListEnvelope)
async def list_my_groups(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
    rows = svc.list_mine(db, user_id=str(current_user.id))
    items = [GroupListItem(id=r["id"], name=r["name"], description=r.get("description")) for r in rows]
    response.headers[Headers.TOTAL_COUNT] = str(len(items))
    return {Keys.ITEMS: items}


# Dependents CRUD
@router.post(Routes.ID + "/dependents", summary="Create dependent", response_model=DependentItem)
@rl_mutation()
async def create_dependent(
    id: str,
    request: Request,
    payload: DependentCreate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: DependentsService = Depends(get_dependents_service),
) -> Dict[str, Any]:
    try:
        data = svc.create(db, group_id=id, actor_id=str(current_user.id), full_name=payload.full_name, dob=payload.dob, email=str(payload.email) if payload.email else None)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return DependentItem(**{
        "id": data.get(Fields.ID),
        "full_name": data.get(Fields.FULL_NAME),
        "dob": data.get(Keys.DOB),
        "email": data.get(Fields.EMAIL),
        "guardian_user_id": data.get(Keys.GUARDIAN_USER_ID),
    })


@router.get(Routes.ID + "/dependents", summary="List dependents", response_model=DependentsEnvelope)
async def list_dependents(
    id: str,
    response: Response,
    limit: int = PaginationConsts.DEFAULT_LIMIT,
    offset: int = PaginationConsts.DEFAULT_OFFSET,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: DependentsService = Depends(get_dependents_service),
) -> Dict[str, Any]:
    limit, offset = clamp_limit_offset(limit, offset, max_limit=PaginationConsts.MAX_LIMIT)
    try:
        result = svc.list(db, group_id=id, actor_id=str(current_user.id), limit=limit, offset=offset)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    items = [DependentItem(**it) for it in result.get(Keys.ITEMS, [])]
    response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
    return {"items": items}


@router.delete(Routes.ID + "/dependents" + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary="Delete dependent")
@rl_mutation()
async def delete_dependent(
    id: str,
    userId: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: DependentsService = Depends(get_dependents_service),
) -> None:
    try:
        svc.delete(db, group_id=id, actor_id=str(current_user.id), dependent_id=userId)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return


@router.post(Routes.ID + "/dependents" + Routes.USER_ID + "/convert", summary="Convert dependent to account", response_model=DependentConvertResponse)
@rl_mutation()
async def convert_dependent(
    id: str,
    userId: str,
    request: Request,
    payload: DependentConvertRequest = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: DependentsService = Depends(get_dependents_service),
) -> Dict[str, Any]:
    try:
        data = svc.convert_to_account(db, group_id=id, actor_id=str(current_user.id), dependent_id=userId, email=(str(payload.email) if payload and payload.email else None))
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return DependentConvertResponse(message=data.get(Keys.MESSAGE, Messages.GROUP_MEMBER_ADDED), userId=data.get(Keys.USER_ID))


@router.get(Routes.ID, summary=Summaries.GROUP_GET, response_model=GroupDetailEnvelope)
async def get_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
    try:
        data = svc.get(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {Keys.DATA: GroupDetail(**{
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_at": data.get("created_at"),
    })}


@router.put(Routes.ID, summary=Summaries.GROUP_UPDATE, response_model=GroupDetailEnvelope)
async def update_group(
    id: str,
    payload: GroupUpdate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: GroupsService = Depends(get_groups_service),
) -> Dict[str, Any]:
    try:
        data = svc.update(db, group_id=id, user_id=str(current_user.id), name=payload.name, description=payload.description)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {Keys.DATA: GroupDetail(**{
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_at": data.get("created_at"),
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
async def list_members(
    id: str,
    response: Response,
    limit: int = PaginationConsts.DEFAULT_LIMIT,
    offset: int = PaginationConsts.DEFAULT_OFFSET,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: MembershipsService = Depends(get_memberships_service),
) -> Dict[str, Any]:
    # Clamp pagination params
    limit, offset = clamp_limit_offset(limit, offset, max_limit=PaginationConsts.MAX_LIMIT)
    try:
        result = svc.list_by_group(db, group_id=id, actor_id=str(current_user.id), limit=limit, offset=offset)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    # Enrich with user details (name/email/age)
    raw_items = result[Keys.ITEMS]
    user_ids = [r.get("user_id") or r.get("userId") or r[Keys.USER_ID] for r in raw_items]
    users_map = {str(u.id): u for u in db.scalars(select(User).where(User.id.in_(user_ids))).all()}
    items = []
    for r in raw_items:
        uid = r.get("user_id") if "user_id" in r else (r.get("userId") or r[Keys.USER_ID])
        u = users_map.get(str(uid))
        items.append(MembershipItem(
            id=r["id"],
            userId=str(uid),
            role=r["role"],
            full_name=(u.full_name if u else None),
            email=(u.email if u else None),
            age=(u.age if u else None),
        ))
    response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
    return {Keys.ITEMS: items}


@router.post(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBER_ADD, response_model=ActionEnvelope)
@rl_mutation()
async def add_member(
    id: str,
    request: Request,
    payload: MemberAdd = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: MembershipsService = Depends(get_memberships_service),
) -> Dict[str, Any]:
    try:
        # Resolve by email for consistency with invitations model; auto-create if missing (scrappy MVP)
        normalized = (payload.email or "").strip().lower()
        temp_password: Optional[str] = None
        target = db.scalar(select(User).where(User.email == normalized))
        if target is None:
            # compute age if dob provided
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
            target = User(
                username=normalized,
                email=normalized,
                password_hash=hash_password(temp_password),
                role=Roles.CAREGIVER,
                full_name=full_name,
                age=age_val,
                corpus_uri=f"user://{normalized}/corpus",
                chat_history_uri=None,
            )
            db.add(target)
            db.commit()
            db.refresh(target)
        svc.add(db, group_id=id, actor_id=str(current_user.id), user_id=str(target.id), role=payload.role or GroupRoles.MEMBER)
        if temp_password:
            logging.getLogger(__name__).info("auto_user_created", extra={"email": normalized, "tempPassword": temp_password, "groupId": id})
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {Keys.MESSAGE: Messages.GROUP_MEMBER_ADDED}


@router.put(Routes.ID + Routes.ACCESS + Routes.USER_ID + Routes.ROLE, summary=Summaries.GROUP_MEMBER_UPDATE, response_model=ActionEnvelope)
@rl_mutation()
async def change_role(
    id: str,
    userId: str,
    request: Request,
    payload: MemberRoleUpdate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: MembershipsService = Depends(get_memberships_service),
) -> Dict[str, Any]:
    try:
        svc.change_role(db, group_id=id, actor_id=str(current_user.id), user_id=userId, role=payload.role)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {Keys.MESSAGE: Messages.GROUP_MEMBER_ROLE_UPDATED}


@router.delete(Routes.ID + Routes.ACCESS + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_MEMBER_REMOVE)
@rl_mutation()
async def remove_member(id: str, userId: str, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
    try:
        svc.remove(db, group_id=id, actor_id=str(current_user.id), user_id=userId)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return


# Group member invites (account members)
@router.post(Routes.ID + Routes.ACCESS + "/invitations", summary="Send group member invite", response_model=GroupMemberInviteCreatedEnvelope)
@rl_mutation()
async def send_group_member_invite(
    id: str,
    request: Request,
    payload: GroupMemberInviteCreate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: GroupMemberInvitesService = Depends(get_group_member_invites_service),
) -> Dict[str, Any]:
    try:
        data = svc.send(db, group_id=id, actor_id=str(current_user.id), email=str(payload.email), full_name=payload.full_name)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {Keys.MESSAGE: Messages.INVITATION_SENT, Keys.DATA: GroupMemberInviteItem(**{
        "id": data.get(Fields.ID),
        "invited_email": data.get(Keys.INVITED_EMAIL),
        "invited_full_name": data.get(Keys.INVITED_FULL_NAME),
        "status": data.get(Keys.STATUS),
        Keys.ACCEPT_URL: data.get(Keys.ACCEPT_URL),
    })}


@router.get(Routes.ID + Routes.ACCESS + "/invitations", summary="List pending group member invites", response_model=GroupMemberInvitesEnvelope)
async def list_group_member_invites(
    id: str,
    response: Response,
    limit: int = PaginationConsts.DEFAULT_LIMIT,
    offset: int = PaginationConsts.DEFAULT_OFFSET,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: GroupMemberInvitesService = Depends(get_group_member_invites_service),
) -> Dict[str, Any]:
    # Any admin can list
    limit, offset = clamp_limit_offset(limit, offset, max_limit=PaginationConsts.MAX_LIMIT)
    try:
        result = svc.list_pending(db, group_id=id, limit=limit, offset=offset)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    items = [GroupMemberInviteItem(**it) for it in result.get(Keys.ITEMS, [])]
    response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
    return {Keys.ITEMS: items}


@router.post(Routes.ID + Routes.ACCESS + Routes.SELF, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_LEAVE)
async def leave_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
    try:
        svc.leave(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return

