from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Body, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Fields
from backend.schemas import UserCreate, UserUpdate, UserResponse
from backend.db.database import get_db
from backend.db.models import User


router = APIRouter(prefix=Prefix.USERS, tags=[Tags.USERS])


@router.get("", summary=Summaries.USERS_LIST)
async def list_users(db: Session = Depends(get_db)) -> Dict[str, Any]:
    users = list(db.scalars(select(User)))
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
        }
        for u in users
    ]
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
    }


@router.put("/{id}", summary=Summaries.USER_UPDATE)
async def update_user(id: str, payload: UserUpdate = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.USER_UPDATED, "id": id, "data": payload.model_dump(exclude_none=True)}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.USER_DELETE)
async def delete_user(id: str) -> None:
    return


