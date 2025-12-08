from typing import Any, Dict
from fastapi import APIRouter, Body, status, Depends
from backend.core.constants import Prefix, Tags, Summaries, Routes
from backend.schemas import MessageCreate, MessageUpdate
from backend.services import MessagesService
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.CHAT_MESSAGES, tags=[Tags.MESSAGES], dependencies=[Depends(get_current_user)])
service = MessagesService()


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.MESSAGE_CREATE)
async def create_message(chatId: str, payload: MessageCreate = Body(default=None)) -> Dict[str, Any]:
    return service.create_message(chatId, payload.model_dump())


@router.get(Routes.ROOT, summary=Summaries.MESSAGE_LIST)
async def list_messages(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "items": service.list_messages(chatId)}


@router.get(Routes.MESSAGE_ID, summary=Summaries.MESSAGE_GET)
async def get_message(chatId: str, messageId: str) -> Dict[str, Any]:
    return service.get_message(chatId, messageId)


@router.put(Routes.MESSAGE_ID, summary=Summaries.MESSAGE_UPDATE)
async def update_message(
    chatId: str, messageId: str, payload: MessageUpdate = Body(default=None)
) -> Dict[str, Any]:
    return service.update_message(chatId, messageId, payload.model_dump(exclude_none=True))


@router.delete(Routes.MESSAGE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.MESSAGE_DELETE)
async def delete_message(chatId: str, messageId: str) -> None:
    service.delete_message(chatId, messageId)
    return


