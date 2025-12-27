from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Body, status, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Fields, Errors, Headers, Keys, Routes
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
            Fields.FULL_NAME: u.full_name,
            Fields.PHONE_NUMBER: u.phone_number,
            Fields.AGE: u.age,
            Fields.COUNTRY: u.country,
            Fields.AVATAR_URI: u.avatar_uri,
            Fields.CREATED_AT: u.created_at,
            Fields.UPDATED_AT: u.updated_at,
            Fields.CORPUS_URI: u.corpus_uri,
            Fields.CHAT_HISTORY_URI: u.chat_history_uri,
            Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == u.id)).all()],
            Fields.ACCOUNT_TYPE: u.account_type,
            Fields.GCP_PROJECT_ID: u.gcp_project_id,
            Fields.TEMP_BUCKET: u.temp_bucket,
            Fields.PAYMENT_INFO: u.payment_info,
        }
        for u in users
    ]
    response.headers[Headers.TOTAL_COUNT] = str(total)
    return {Keys.ITEMS: items}


@router.post("", status_code=status.HTTP_201_CREATED, summary=Summaries.USER_CREATE)
async def create_user(payload: UserCreate = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.USER_CREATED, Keys.DATA: payload.model_dump()}


@router.get("/{id}", summary=Summaries.USER_GET, response_model=UserResponse)
async def get_user(id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        uuid = UUID(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    user = db.scalar(select(User).where(User.id == uuid))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    return {
        Fields.ID: user.id,
        Fields.USERNAME: user.username,
        Fields.EMAIL: user.email,
        Fields.ROLE: user.role,
        Fields.FULL_NAME: user.full_name,
        Fields.PHONE_NUMBER: user.phone_number,
        Fields.AGE: user.age,
        Fields.COUNTRY: user.country,
        Fields.AVATAR_URI: user.avatar_uri,
        Fields.CREATED_AT: user.created_at,
        Fields.UPDATED_AT: user.updated_at,
        Fields.CORPUS_URI: user.corpus_uri,
        Fields.CHAT_HISTORY_URI: user.chat_history_uri,
        Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == user.id)).all()],
        Fields.ACCOUNT_TYPE: user.account_type,
        Fields.GCP_PROJECT_ID: user.gcp_project_id,
        Fields.TEMP_BUCKET: user.temp_bucket,
        Fields.PAYMENT_INFO: user.payment_info,
    }

@router.post(f"/{{id}}{Routes.AVATAR}", status_code=status.HTTP_201_CREATED, summary=Summaries.AVATAR_UPLOAD)
async def upload_avatar(
    id: str,
    file: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        uuid = UUID(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    if current_user.id != uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    if not current_user.temp_bucket:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.MISSING_INGESTION_CONFIG)
    fname = (file.filename or "avatar").split("/")[-1]
    avatar_uri = f"gs://{current_user.temp_bucket}/avatars/{current_user.id}/{fname}"
    current_user.avatar_uri = avatar_uri
    db.commit()
    db.refresh(current_user)
    return {Fields.ID: current_user.id, Fields.AVATAR_URI: current_user.avatar_uri}

@router.put("/{id}", summary=Summaries.USER_UPDATE)
async def update_user(id: str, payload: UserUpdate = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.USER_UPDATED, Fields.ID: id, Keys.DATA: payload.model_dump(exclude_none=True)}


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
        raise HTTPException(status_code=404, detail=Errors.USER_NOT_FOUND)
    if current_user.id != uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)
    user = db.scalar(select(User).where(User.id == uuid))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.USER_NOT_FOUND)
    data = payload.model_dump(exclude_none=True)
    if Fields.FULL_NAME in data:
        user.full_name = data[Fields.FULL_NAME]
    if Fields.PHONE_NUMBER in data:
        user.phone_number = data[Fields.PHONE_NUMBER]
    if Fields.AGE in data:
        user.age = data[Fields.AGE]
    if Fields.COUNTRY in data:
        user.country = data[Fields.COUNTRY]
    if Fields.AVATAR_URI in data:
        user.avatar_uri = data[Fields.AVATAR_URI]
    if Fields.CORPUS_URI in data:
        user.corpus_uri = data[Fields.CORPUS_URI]
    if Fields.CHAT_HISTORY_URI in data:
        user.chat_history_uri = data[Fields.CHAT_HISTORY_URI]
    if Fields.ACCOUNT_TYPE in data:
        user.account_type = data[Fields.ACCOUNT_TYPE]
    if Fields.GCP_PROJECT_ID in data:
        user.gcp_project_id = data[Fields.GCP_PROJECT_ID]
    if Fields.TEMP_BUCKET in data:
        user.temp_bucket = data[Fields.TEMP_BUCKET]
    if Fields.PAYMENT_INFO in data:
        user.payment_info = data[Fields.PAYMENT_INFO]
    db.commit()
    db.refresh(user)
    return {
        Fields.ID: user.id,
        Fields.USERNAME: user.username,
        Fields.EMAIL: user.email,
        Fields.ROLE: user.role,
        Fields.FULL_NAME: user.full_name,
        Fields.PHONE_NUMBER: user.phone_number,
        Fields.AGE: user.age,
        Fields.COUNTRY: user.country,
        Fields.AVATAR_URI: user.avatar_uri,
        Fields.CREATED_AT: user.created_at,
        Fields.UPDATED_AT: user.updated_at,
        Fields.CORPUS_URI: user.corpus_uri,
        Fields.CHAT_HISTORY_URI: user.chat_history_uri,
        Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == user.id)).all()],
        Fields.ACCOUNT_TYPE: user.account_type,
        Fields.GCP_PROJECT_ID: user.gcp_project_id,
        Fields.TEMP_BUCKET: user.temp_bucket,
        Fields.PAYMENT_INFO: user.payment_info,
    }


