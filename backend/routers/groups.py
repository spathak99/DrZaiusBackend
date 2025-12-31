from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, Routes, GroupRoles, Messages, Headers, Pagination as PaginationConsts
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_groups_service, get_memberships_service, get_group_member_invites_service, get_dependents_service
from backend.db.models import User
from backend.services.groups_service import GroupsService, MembershipsService
from backend.services.group_member_invites_service import GroupMemberInvitesService
from backend.services.dependents_service import DependentsService
from backend.utils.pagination import clamp_limit_offset
from backend.routers.http_errors import status_for_error
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
)

router = APIRouter(prefix=Prefix.GROUPS, tags=[Tags.GROUPS], dependencies=[Depends(get_current_user)])


class MemberAdd(BaseModel):
    email: str
    role: Optional[str] = None


class MemberRoleUpdate(BaseModel):
    role: str


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.GROUP_CREATE, response_model=GroupDetailEnvelope)
async def create_group(
    payload: GroupCreate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: GroupsService = Depends(get_groups_service),
) -> Dict[str, Any]:
    data = svc.create(db, name=payload.name, description=payload.description, created_by=str(current_user.id))
    return {"data": GroupDetail(**{
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_at": data.get("created_at"),
    })}


@router.get(Routes.ROOT, summary=Summaries.GROUPS_LIST, response_model=GroupsListEnvelope)
async def list_my_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
    rows = svc.list_mine(db, user_id=str(current_user.id))
    items = [GroupListItem(id=r["id"], name=r["name"], description=r.get("description")) for r in rows]
    return {"items": items}


# Dependents CRUD
@router.post(Routes.ID + "/dependents", summary="Create dependent", response_model=DependentItem)
async def create_dependent(
    id: str,
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
async def delete_dependent(
    id: str,
    userId: str,
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


@router.get(Routes.ID, summary=Summaries.GROUP_GET, response_model=GroupDetailEnvelope)
async def get_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: GroupsService = Depends(get_groups_service)) -> Dict[str, Any]:
    try:
        data = svc.get(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {"data": GroupDetail(**{
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
    return {"data": GroupDetail(**{
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
async def add_member(
    id: str,
    payload: MemberAdd = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    svc: MembershipsService = Depends(get_memberships_service),
) -> Dict[str, Any]:
    try:
        # Resolve by email for consistency with invitations model
        target = db.scalar(select(User).where(User.email == payload.email))
        if target is None:
            raise ValueError(Errors.USER_NOT_FOUND)
        svc.add(db, group_id=id, actor_id=str(current_user.id), user_id=str(target.id), role=payload.role or GroupRoles.MEMBER)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return {"message": Messages.GROUP_MEMBER_ADDED}


@router.put(Routes.ID + Routes.ACCESS + Routes.USER_ID + Routes.ROLE, summary=Summaries.GROUP_MEMBER_UPDATE, response_model=ActionEnvelope)
async def change_role(
    id: str,
    userId: str,
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
    return {"message": Messages.GROUP_MEMBER_ROLE_UPDATED}


@router.delete(Routes.ID + Routes.ACCESS + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_MEMBER_REMOVE)
async def remove_member(id: str, userId: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
    try:
        svc.remove(db, group_id=id, actor_id=str(current_user.id), user_id=userId)
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return


# Group member invites (account members)
@router.post(Routes.ID + Routes.ACCESS + "/invitations", summary="Send group member invite", response_model=GroupMemberInviteCreatedEnvelope)
async def send_group_member_invite(
    id: str,
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
    return {"message": Messages.INVITATION_SENT, "data": GroupMemberInviteItem(**{
        "id": data.get(Fields.ID),
        "invited_email": data.get(Keys.INVITED_EMAIL),
        "invited_full_name": data.get(Keys.INVITED_FULL_NAME),
        "status": data.get(Keys.STATUS),
        "acceptUrl": data.get(Keys.ACCEPT_URL),
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
    items = [GroupMemberInviteItem(**it) for it in result.get("items", [])]
    response.headers[Headers.TOTAL_COUNT] = str(result.get("total", len(items)))
    return {"items": items}


@router.post(Routes.ID + Routes.ACCESS + Routes.SELF, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_LEAVE)
async def leave_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
    try:
        svc.leave(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return

