from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Errors, Routes, Fields
from backend.db.database import get_db
from backend.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse
from backend.services.auth_service import AuthService
from sqlalchemy import select
from backend.db.models import User, GroupMembership
from backend.core.constants import Auth as AuthConst


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
            corpus_uri=payload.corpus_uri,
            chat_history_uri=payload.chat_history_uri,
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
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
    scheme, _, token = authorization.partition(" ")
    if not token or scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
    try:
        payload = service.verify_token(token)
        user_id = payload.get(AuthConst.JWT_CLAIM_SUB)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        user = db.scalar(select(User).where(User.id == user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
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
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.INVALID_CREDENTIALS)


@router.post(Routes.AUTH_LOGOUT, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.LOGOUT)
async def logout() -> None:
    return


