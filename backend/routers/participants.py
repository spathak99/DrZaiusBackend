from typing import Any, Dict
from fastapi import APIRouter, Body, status, Depends
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.CHAT_PARTICIPANTS, tags=[Tags.PARTICIPANTS], dependencies=[Depends(get_current_user)])


@router.get(Routes.ROOT, summary=Summaries.PARTICIPANTS_LIST)
async def list_participants(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "items": []}


@router.post(Routes.ROOT, summary=Summaries.PARTICIPANTS_ADD)
async def add_participant(chatId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.PARTICIPANT_ADDED, "chatId": chatId, "data": payload}


@router.delete(Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.PARTICIPANTS_REMOVE)
async def remove_participant(chatId: str, userId: str) -> None:
    return


