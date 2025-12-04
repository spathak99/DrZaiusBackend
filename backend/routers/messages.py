from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags
from backend.schemas import MessageCreate, MessageUpdate
from backend.services import MessagesService


router = APIRouter(prefix=Prefix.CHAT_MESSAGES, tags=[Tags.MESSAGES])
service = MessagesService()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create message in chat")
async def create_message(chatId: str, payload: MessageCreate = Body(default=None)) -> Dict[str, Any]:
    return service.create_message(chatId, payload.model_dump())


@router.get("", summary="List messages in chat")
async def list_messages(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "items": service.list_messages(chatId)}


@router.get("/{messageId}", summary="Get message by ID")
async def get_message(chatId: str, messageId: str) -> Dict[str, Any]:
    return service.get_message(chatId, messageId)


@router.put("/{messageId}", summary="Update message by ID")
async def update_message(
    chatId: str, messageId: str, payload: MessageUpdate = Body(default=None)
) -> Dict[str, Any]:
    return service.update_message(chatId, messageId, payload.model_dump(exclude_none=True))


@router.delete(
    "/{messageId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete message by ID",
)
async def delete_message(chatId: str, messageId: str) -> None:
    service.delete_message(chatId, messageId)
    return


