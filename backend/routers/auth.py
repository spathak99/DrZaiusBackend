from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags


router = APIRouter(prefix=Prefix.AUTH, tags=[Tags.AUTH])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
async def signup(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": "signup successful", "data": payload}


@router.post("/login", summary="Log in and receive authentication token")
async def login(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"access_token": "fake-token", "token_type": "bearer"}


@router.get("/me", summary="Get current user")
async def auth_me() -> Dict[str, Any]:
    return {"id": "current-user-id", "username": "current_user"}


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out and invalidate token",
)
async def logout() -> None:
    return


