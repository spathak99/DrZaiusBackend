from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags


router = APIRouter(prefix=Prefix.CHAT_PARTICIPANTS, tags=[Tags.PARTICIPANTS])


@router.get("", summary="List participants in a chat")
async def list_participants(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "items": []}


@router.post("", summary="Add participant to a chat")
async def add_participant(chatId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": "participant added", "chatId": chatId, "data": payload}


@router.delete(
    "/{userId}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove participant from a chat"
)
async def remove_participant(chatId: str, userId: str) -> None:
    return


