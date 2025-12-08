from typing import Any, Dict
from fastapi import APIRouter, status
from backend.core.constants import Prefix, Tags, Summaries, Routes


router = APIRouter(prefix=Prefix.USER_CHATS, tags=[Tags.USER_CHATS])


@router.get(Routes.ROOT, summary=Summaries.LIST_CHATS)
async def list_user_chats(userId: str) -> Dict[str, Any]:
    return {"userId": userId, "items": []}


@router.get(Routes.ID, summary=Summaries.GET_CHAT)
async def get_user_chat(userId: str, id: str) -> Dict[str, Any]:
    return {"userId": userId, "id": id}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.DELETE_CHAT)
async def delete_user_chat(userId: str, id: str) -> None:
    return


