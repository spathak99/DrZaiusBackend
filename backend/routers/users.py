from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Body, status, Depends, HTTPException, Response
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Fields, Errors
from backend.schemas import UserCreate, UserUpdate, UserResponse
from backend.db.database import get_db
from backend.db.models import User, GroupMembership
from backend.routers.deps import get_current_user
from backend.schemas.user import UserSettingsUpdate


router = APIRouter(prefix=Prefix.USERS, tags=[Tags.USERS])


@router.get("", summary=Summaries.USERS_LIST)
async def list_users(
    response: Response,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = db.scalars(
        select(User).order_by(User.created_at).limit(limit).offset(offset)
    ).all()
    items: List[Dict[str, Any]] = [
        {
            Fields.ID: u.id,
            Fields.USERNAME: u.username,
            Fields.EMAIL: u.email,
            Fields.ROLE: u.role,
            Fields.CREATED_AT: u.created_at,
            Fields.UPDATED_AT: u.updated_at,
            Fields.CORPUS_URI: u.corpus_uri,
            Fields.CHAT_HISTORY_URI: u.chat_history_uri,
            Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == u.id)).all()],
        }
        for u in users
    ]
    response.headers["X-Total-Count"] = str(total)
    return {"items": items}


@router.post("", status_code=status.HTTP_201_CREATED, summary=Summaries.USER_CREATE)
async def create_user(payload: UserCreate = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.USER_CREATED, "data": payload.model_dump()}


@router.get("/{id}", summary=Summaries.USER_GET, response_model=UserResponse)
async def get_user(id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        uuid = UUID(id)
    except Exception:
        raise HTTPException(status_code=404, detail="not_found")
    user = db.scalar(select(User).where(User.id == uuid))
    if user is None:
        raise HTTPException(status_code=404, detail="not_found")
    return {
        Fields.ID: user.id,
        Fields.USERNAME: user.username,
        Fields.EMAIL: user.email,
        Fields.ROLE: user.role,
        Fields.CREATED_AT: user.created_at,
        Fields.UPDATED_AT: user.updated_at,
        Fields.CORPUS_URI: user.corpus_uri,
        Fields.CHAT_HISTORY_URI: user.chat_history_uri,
        Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == user.id)).all()],
    }


@router.put("/{id}", summary=Summaries.USER_UPDATE)
async def update_user(id: str, payload: UserUpdate = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.USER_UPDATED, "id": id, "data": payload.model_dump(exclude_none=True)}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.USER_DELETE)
async def delete_user(id: str) -> None:
    return


@router.patch("/{id}", summary=Summaries.USER_UPDATE, response_model=UserResponse)
async def patch_user(
    id: str,
    payload: UserSettingsUpdate = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        uuid = UUID(id)
    except Exception:
        raise HTTPException(status_code=404, detail="not_found")
    if current_user.id != uuid:
        raise HTTPException(status_code=403, detail=Errors.FORBIDDEN)
    user = db.scalar(select(User).where(User.id == uuid))
    if user is None:
        raise HTTPException(status_code=404, detail="not_found")
    data = payload.model_dump(exclude_none=True)
    if "corpus_uri" in data:
        user.corpus_uri = data["corpus_uri"]
    if "chat_history_uri" in data:
        user.chat_history_uri = data["chat_history_uri"]
    db.commit()
    db.refresh(user)
    return {
        Fields.ID: user.id,
        Fields.USERNAME: user.username,
        Fields.EMAIL: user.email,
        Fields.ROLE: user.role,
        Fields.CREATED_AT: user.created_at,
        Fields.UPDATED_AT: user.updated_at,
        Fields.CORPUS_URI: user.corpus_uri,
        Fields.CHAT_HISTORY_URI: user.chat_history_uri,
        Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == user.id)).all()],
    }


