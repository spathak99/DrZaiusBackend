from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages
from backend.schemas import UserCreate, UserUpdate


router = APIRouter(prefix=Prefix.USERS, tags=[Tags.USERS])


@router.get("", summary=Summaries.USERS_LIST)
async def list_users() -> Dict[str, Any]:
    return {"items": []}


@router.post("", status_code=status.HTTP_201_CREATED, summary=Summaries.USER_CREATE)
async def create_user(payload: UserCreate = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.USER_CREATED, "data": payload.model_dump()}


@router.get("/{id}", summary=Summaries.USER_GET)
async def get_user(id: str) -> Dict[str, Any]:
    return {"id": id}


@router.put("/{id}", summary=Summaries.USER_UPDATE)
async def update_user(id: str, payload: UserUpdate = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.USER_UPDATED, "id": id, "data": payload.model_dump(exclude_none=True)}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.USER_DELETE)
async def delete_user(id: str) -> None:
    return


