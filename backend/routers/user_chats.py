from typing import Any, Dict
from fastapi import APIRouter
from backend.core.constants import Prefix, Tags, Summaries


router = APIRouter(prefix=Prefix.USER_CHATS, tags=[Tags.USER_CHATS])


@router.get("", summary=Summaries.LIST_CHATS)
async def list_user_chats(userId: str) -> Dict[str, Any]:
    return {"userId": userId, "items": []}


@router.get("/{id}", summary=Summaries.GET_CHAT)
async def get_user_chat(userId: str, id: str) -> Dict[str, Any]:
    return {"userId": userId, "id": id}


@router.delete("/{id}", status_code=204, summary=Summaries.DELETE_CHAT)
async def delete_user_chat(userId: str, id: str) -> None:
    return


