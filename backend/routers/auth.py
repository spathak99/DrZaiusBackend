from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Errors, Routes, Fields
from backend.db.database import get_db
from backend.schemas import SignupRequest, LoginRequest, ChangePasswordRequest, TokenResponse, UserResponse
from backend.services.auth_service import AuthService
from sqlalchemy import select
from backend.db.models import User, GroupMembership
from backend.core.constants import Auth as AuthConst
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.AUTH, tags=[Tags.AUTH])
service = AuthService()


@router.post(Routes.AUTH_SIGNUP, status_code=status.HTTP_201_CREATED, summary=Summaries.SIGNUP, response_model=TokenResponse)
async def signup(payload: SignupRequest = Body(default=None), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        _, token = service.signup(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
            role=payload.role.value,
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            age=payload.age,
            country=payload.country,
            avatar_uri=payload.avatar_uri,
            corpus_uri=payload.corpus_uri,
            chat_history_uri=payload.chat_history_uri,
            account_type=(payload.account_type.value if payload.account_type else None),
            group_id=payload.group_id,
            gcp_project_id=payload.gcp_project_id,
            temp_bucket=payload.temp_bucket,
            payment_info=payload.payment_info,
        )
        return {"access_token": token, "token_type": Messages.TOKEN_TYPE_BEARER}
    except ValueError as e:
        if str(e) in {Errors.USERNAME_TAKEN, Errors.EMAIL_TAKEN}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise


@router.post(Routes.AUTH_LOGIN, summary=Summaries.LOGIN, response_model=TokenResponse)
async def login(payload: LoginRequest = Body(default=None), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        _, token = service.login(db, username=payload.username, password=payload.password)
        return {"access_token": token, "token_type": Messages.TOKEN_TYPE_BEARER}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.INVALID_CREDENTIALS)


@router.get(Routes.AUTH_ME, summary=Summaries.AUTH_ME, response_model=UserResponse)
async def auth_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    user = current_user
    return {
        Fields.ID: user.id,
        Fields.USERNAME: user.username,
        Fields.EMAIL: user.email,
        Fields.ROLE: user.role,
        Fields.CREATED_AT: user.created_at,
        Fields.UPDATED_AT: user.updated_at,
        Fields.FULL_NAME: user.full_name,
        Fields.PHONE_NUMBER: user.phone_number,
        Fields.AGE: user.age,
        Fields.COUNTRY: user.country,
        Fields.AVATAR_URI: user.avatar_uri,
        Fields.CORPUS_URI: user.corpus_uri,
        Fields.CHAT_HISTORY_URI: user.chat_history_uri,
        Fields.GROUP_IDS: [m.group_id for m in db.scalars(select(GroupMembership).where(GroupMembership.user_id == user.id)).all()],
        Fields.ACCOUNT_TYPE: user.account_type,
        Fields.GROUP_ID: user.group_id,
        Fields.GCP_PROJECT_ID: user.gcp_project_id,
        Fields.TEMP_BUCKET: user.temp_bucket,
        Fields.PAYMENT_INFO: user.payment_info,
    }


@router.post(Routes.AUTH_LOGOUT, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.LOGOUT)
async def logout() -> None:
    return


@router.post(Routes.AUTH_CHANGE_PASSWORD, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.CHANGE_PASSWORD)
async def change_password(
    payload: ChangePasswordRequest = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        service.change_password(
            db,
            user=current_user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except ValueError as e:
        if str(e) == Errors.INCORRECT_PASSWORD:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.INCORRECT_PASSWORD)
        raise
    return

