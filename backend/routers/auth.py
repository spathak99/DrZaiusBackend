from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages


router = APIRouter(prefix=Prefix.AUTH, tags=[Tags.AUTH])


@router.post("/signup", status_code=status.HTTP_201_CREATED, summary=Summaries.SIGNUP)
async def signup(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.SIGNUP_SUCCESSFUL, "data": payload}


@router.post("/login", summary=Summaries.LOGIN)
async def login(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"access_token": Messages.ACCESS_TOKEN_FAKE, "token_type": Messages.TOKEN_TYPE_BEARER}


@router.get("/me", summary=Summaries.AUTH_ME)
async def auth_me() -> Dict[str, Any]:
    return {"id": "current-user-id", "username": "current_user"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.LOGOUT)
async def logout() -> None:
    return


