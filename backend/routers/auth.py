from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Errors
from backend.db.database import get_db
from backend.schemas import SignupRequest, LoginRequest, TokenResponse
from backend.services.auth_service import AuthService


router = APIRouter(prefix=Prefix.AUTH, tags=[Tags.AUTH])
service = AuthService()


@router.post("/signup", status_code=status.HTTP_201_CREATED, summary=Summaries.SIGNUP, response_model=TokenResponse)
async def signup(payload: SignupRequest = Body(default=None), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        _, token = service.signup(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
            role=payload.role.value,
            storage_root_uri=payload.storage_root_uri,
            storage_provider=payload.storage_provider.value,
            storage_metadata=payload.storage_metadata,
        )
        return {"access_token": token, "token_type": Messages.TOKEN_TYPE_BEARER}
    except ValueError as e:
        if str(e) in {Errors.USERNAME_TAKEN, Errors.EMAIL_TAKEN}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise


@router.post("/login", summary=Summaries.LOGIN, response_model=TokenResponse)
async def login(payload: LoginRequest = Body(default=None), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        _, token = service.login(db, username=payload.username, password=payload.password)
        return {"access_token": token, "token_type": Messages.TOKEN_TYPE_BEARER}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.INVALID_CREDENTIALS)


@router.get("/me", summary=Summaries.AUTH_ME)
async def auth_me() -> Dict[str, Any]:
    # Placeholder: implement token parsing and user lookup later
    return {"message": "not_implemented"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.LOGOUT)
async def logout() -> None:
    return


