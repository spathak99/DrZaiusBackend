from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages


router = APIRouter(prefix=Prefix.CHAT_PARTICIPANTS, tags=[Tags.PARTICIPANTS])


@router.get("", summary=Summaries.PARTICIPANTS_LIST)
async def list_participants(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "items": []}


@router.post("", summary=Summaries.PARTICIPANTS_ADD)
async def add_participant(chatId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.PARTICIPANT_ADDED, "chatId": chatId, "data": payload}


@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.PARTICIPANTS_REMOVE)
async def remove_participant(chatId: str, userId: str) -> None:
    return


