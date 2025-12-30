from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, Routes, GroupRoles, Messages, Headers, Pagination as PaginationConsts
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_groups_service, get_memberships_service
from backend.db.models import User
from backend.services.groups_service import GroupsService, MembershipsService
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
    items = [MembershipItem(id=r["id"], userId=r["user_id"] if "user_id" in r else r.get("userId") or r[Keys.USER_ID], role=r["role"]) for r in result[Keys.ITEMS]]  # tolerate key naming
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


@router.post(Routes.ID + Routes.ACCESS + Routes.SELF, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_LEAVE)
async def leave_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: MembershipsService = Depends(get_memberships_service)) -> None:
    try:
        svc.leave(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=status_for_error(detail), detail=detail)
    return

