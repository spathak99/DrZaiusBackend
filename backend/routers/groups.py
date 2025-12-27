from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, GroupRoles, Routes, Headers
from backend.db.database import get_db
from backend.db.models import User, Group, GroupMembership
from backend.routers.deps import get_current_user
from backend.schemas import GroupCreate, GroupResponse, GroupMemberAdd
from pydantic import BaseModel
from typing import Optional


router = APIRouter(prefix=Prefix.GROUPS, tags=[Tags.GROUPS], dependencies=[Depends(get_current_user)])


def _is_admin(db: Session, group_id: UUID, user_id: UUID) -> bool:
    membership = db.scalar(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id, GroupMembership.user_id == user_id
        )
    )
    return bool(membership and membership.role == GroupRoles.ADMIN)

def _get_existing_admin(db: Session, group_id: UUID) -> Optional[GroupMembership]:
    return db.scalar(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id, GroupMembership.role == GroupRoles.ADMIN
        )
    )

@router.get(Routes.ROOT, summary=Summaries.GROUPS_LIST)
async def list_my_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    memberships = db.scalars(select(GroupMembership).where(GroupMembership.user_id == current_user.id)).all()
    group_ids = [m.group_id for m in memberships]
    groups = db.scalars(select(Group).where(Group.id.in_(group_ids))).all() if group_ids else []
    items: List[Dict[str, Any]] = [
        {
            Fields.ID: g.id,
            Fields.NAME: g.name,
            Fields.DESCRIPTION: g.description,
            Fields.CREATED_BY: g.created_by,
            Fields.CREATED_AT: g.created_at,
            Fields.UPDATED_AT: g.updated_at,
        }
        for g in groups
    ]
    return {Keys.ITEMS: items}


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.GROUP_CREATE)
async def create_group(payload: GroupCreate = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    group = Group(name=payload.name, description=payload.description, created_by=current_user.id)
    db.add(group)
    db.flush()
    # creator is admin
    membership = GroupMembership(group_id=group.id, user_id=current_user.id, role=GroupRoles.ADMIN)
    db.add(membership)
    db.commit()
    db.refresh(group)
    return {
        Fields.ID: group.id,
        Fields.NAME: group.name,
        Fields.DESCRIPTION: group.description,
        Fields.CREATED_BY: group.created_by,
        Fields.CREATED_AT: group.created_at,
        Fields.UPDATED_AT: group.updated_at,
    }


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.patch(Routes.ID, summary=Summaries.GROUP_UPDATE)
async def patch_group(
    id: str,
    payload: GroupUpdate = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    group = db.scalar(select(Group).where(Group.id == id))
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.GROUP_NOT_FOUND)
    if not _is_admin(db, group.id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    data = payload.model_dump(exclude_none=True)
    if Fields.NAME in data:
        group.name = data[Fields.NAME]
    if Fields.DESCRIPTION in data:
        group.description = data[Fields.DESCRIPTION]
    db.commit()
    db.refresh(group)
    return {
        Fields.ID: group.id,
        Fields.NAME: group.name,
        Fields.DESCRIPTION: group.description,
        Fields.CREATED_BY: group.created_by,
        Fields.CREATED_AT: group.created_at,
        Fields.UPDATED_AT: group.updated_at,
    }


@router.get(Routes.ID, summary=Summaries.GROUP_GET)
async def get_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        group = db.scalar(select(Group).where(Group.id == id))
    except Exception:
        group = None
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.GROUP_NOT_FOUND)
    return {
        Fields.ID: group.id,
        Fields.NAME: group.name,
        Fields.DESCRIPTION: group.description,
        Fields.CREATED_BY: group.created_by,
        Fields.CREATED_AT: group.created_at,
        Fields.UPDATED_AT: group.updated_at,
    }


@router.get(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBERS_LIST)
async def list_members(
    id: str,
    response: Response,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    group = db.scalar(select(Group).where(Group.id == id))
    if group is None:
        raise HTTPException(status_code=404, detail=Errors.GROUP_NOT_FOUND)
    total = db.scalar(
        select(func.count()).select_from(GroupMembership).where(GroupMembership.group_id == group.id)
    ) or 0
    memberships = db.scalars(
        select(GroupMembership)
        .where(GroupMembership.group_id == group.id)
        .order_by(GroupMembership.created_at)
        .limit(limit)
        .offset(offset)
    ).all()
    items = [
        {Fields.USER_ID: m.user_id, Fields.ACCESS_LEVEL: m.role, Fields.CREATED_AT: m.created_at, Fields.UPDATED_AT: m.updated_at}
        for m in memberships
    ]
    response.headers[Headers.TOTAL_COUNT] = str(total)
    return {Keys.GROUP_ID: group.id, Keys.ITEMS: items}


@router.post(Routes.ID + Routes.ACCESS, summary=Summaries.GROUP_MEMBER_ADD)
async def add_member(id: str, payload: GroupMemberAdd = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    group = db.scalar(select(Group).where(Group.id == id))
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.GROUP_NOT_FOUND)
    if not _is_admin(db, group.id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    user = db.scalar(select(User).where(User.id == payload.user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    # upsert-like: check if exists
    existing = db.scalar(
        select(GroupMembership).where(
            GroupMembership.group_id == group.id, GroupMembership.user_id == payload.user_id
        )
    )
    desired_role = payload.role or GroupRoles.MEMBER
    if desired_role == GroupRoles.ADMIN:
        current_admin = _get_existing_admin(db, group.id)
        if current_admin and current_admin.user_id != payload.user_id:
            # only one admin allowed
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Errors.GROUP_ADMIN_EXISTS)
    if existing is None:
        membership = GroupMembership(group_id=group.id, user_id=payload.user_id, role=desired_role)
        db.add(membership)
    else:
        # Prevent creating multiple admins
        if desired_role == GroupRoles.ADMIN:
            current_admin = _get_existing_admin(db, group.id)
            if current_admin and current_admin.user_id != payload.user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Errors.GROUP_ADMIN_EXISTS)
        existing.role = desired_role or existing.role or GroupRoles.MEMBER
    db.commit()
    return {Keys.GROUP_ID: group.id, Fields.USER_ID: str(payload.user_id)}


@router.delete(Routes.ID + Routes.ACCESS + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_MEMBER_REMOVE)
async def remove_member(id: str, userId: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    group = db.scalar(select(Group).where(Group.id == id))
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.GROUP_NOT_FOUND)
    if not _is_admin(db, group.id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    membership = db.scalar(
        select(GroupMembership).where(GroupMembership.group_id == group.id, GroupMembership.user_id == userId)
    )
    if membership:
        db.delete(membership)
        db.commit()
    return


@router.delete(Routes.ID + Routes.ACCESS + Routes.SELF, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.GROUP_LEAVE)
async def leave_group(id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    group = db.scalar(select(Group).where(Group.id == id))
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.GROUP_NOT_FOUND)
    membership = db.scalar(
        select(GroupMembership).where(
            GroupMembership.group_id == group.id, GroupMembership.user_id == current_user.id
        )
    )
    if membership is None:
        # Idempotent leave
        return
    # If user is admin, ensure at least one other admin remains
    if membership.role == GroupRoles.ADMIN:
        admin_count = db.scalar(
            select(func.count()).select_from(GroupMembership).where(
                GroupMembership.group_id == group.id, GroupMembership.role == GroupRoles.ADMIN
            )
        ) or 0
        if admin_count <= 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    db.delete(membership)
    db.commit()
    return


