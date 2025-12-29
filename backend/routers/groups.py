from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, Routes, GroupRoles, Messages
from backend.db.database import get_db
from backend.routers.deps import get_current_user
from backend.db.models import User
from backend.services.groups_service import GroupsService, MembershipsService
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


def _raise(detail: str) -> None:
    code = status.HTTP_400_BAD_REQUEST
    if detail == Errors.FORBIDDEN:
        code = status.HTTP_403_FORBIDDEN
    if detail in (Errors.GROUP_NOT_FOUND, Errors.USER_NOT_FOUND):
        code = status.HTTP_404_NOT_FOUND
    raise HTTPException(status_code=code, detail=detail)


class MemberAdd(BaseModel):
    userId: str
    role: Optional[str] = None


class MemberRoleUpdate(BaseModel):
    role: str


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.GROUP_CREATE, response_model=GroupDetailEnvelope)
async def create_group(
    payload: GroupCreate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    svc = GroupsService()
    data = svc.create(db, name=payload.name, description=payload.description, created_by=str(current_user.id))
    return {"data": GroupDetail(**{
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_at": data.get("created_at"),
    })}


@router.get(Routes.ROOT, summary=Summaries.GROUPS_LIST, response_model=GroupsListEnvelope)
async def list_my_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    svc = GroupsService()
    rows = svc.list_mine(db, user_id=str(current_user.id))
    items = [GroupListItem(id=r["id"], name=r["name"], description=r.get("description")) for r in rows]
    return {"items": items}


@router.get(Routes.ID, summary=Summaries.GROUP_GET, response_model=GroupDetailEnvelope)
async def get_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    svc = GroupsService()
    try:
        data = svc.get(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        _raise(str(e))
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
) -> Dict[str, Any]:
    svc = GroupsService()
    try:
        data = svc.update(db, group_id=id, user_id=str(current_user.id), name=payload.name, description=payload.description)
    except ValueError as e:
        _raise(str(e))
    return {"data": GroupDetail(**{
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_at": data.get("created_at"),
    })}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_DELETE)
async def delete_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    svc = GroupsService()
    try:
        svc.delete(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        _raise(str(e))
    return


@router.get(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBERS_LIST, response_model=MembershipsListEnvelope)
async def list_members(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    svc = MembershipsService()
    try:
        rows = svc.list_by_group(db, group_id=id, actor_id=str(current_user.id))
    except ValueError as e:
        _raise(str(e))
    items = [MembershipItem(id=r["id"], userId=r["user_id"] if "user_id" in r else r.get("userId") or r[Keys.USER_ID], role=r["role"]) for r in rows]  # tolerate key naming
    return {"items": items}


@router.post(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBER_ADD, response_model=ActionEnvelope)
async def add_member(
    id: str,
    payload: MemberAdd = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    svc = MembershipsService()
    try:
        svc.add(db, group_id=id, actor_id=str(current_user.id), user_id=payload.userId, role=payload.role or GroupRoles.MEMBER)
    except ValueError as e:
        _raise(str(e))
    return {"message": Messages.GROUP_MEMBER_ADDED}


@router.put(Routes.ID + Routes.ACCESS + Routes.USER_ID + "/role", summary=Summaries.GROUP_MEMBER_UPDATE, response_model=ActionEnvelope)
async def change_role(
    id: str,
    userId: str,
    payload: MemberRoleUpdate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    svc = MembershipsService()
    try:
        svc.change_role(db, group_id=id, actor_id=str(current_user.id), user_id=userId, role=payload.role)
    except ValueError as e:
        _raise(str(e))
    return {"message": Messages.GROUP_MEMBER_ROLE_UPDATED}


@router.delete(Routes.ID + Routes.ACCESS + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_MEMBER_REMOVE)
async def remove_member(id: str, userId: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    svc = MembershipsService()
    try:
        svc.remove(db, group_id=id, actor_id=str(current_user.id), user_id=userId)
    except ValueError as e:
        _raise(str(e))
    return


@router.post(Routes.ID + Routes.ACCESS + Routes.SELF, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_LEAVE)
async def leave_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    svc = MembershipsService()
    try:
        svc.leave(db, group_id=id, user_id=str(current_user.id))
    except ValueError as e:
        _raise(str(e))
    return

