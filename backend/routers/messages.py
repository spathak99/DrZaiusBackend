from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, status, Depends, HTTPException
from backend.core.constants import Prefix, Tags, Summaries, Routes, Keys, ChatKeys, Errors
from backend.schemas import MessageCreate, MessageUpdate
from backend.services import ChatHistoryService
from backend.routers.deps import get_current_user
from backend.db.models import User


router = APIRouter(prefix=Prefix.CHAT_MESSAGES, tags=[Tags.MESSAGES], dependencies=[Depends(get_current_user)])
history = ChatHistoryService()


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.MESSAGE_CREATE)
async def create_message(
    chatId: str,
    payload: MessageCreate = Body(default=None),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    if not current_user.chat_history_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.CHAT_HISTORY_URI_NOT_SET)
    body = payload.model_dump()
    return history.create_message(
        history_uri=current_user.chat_history_uri,
        chat_id=chatId,
        content=body.get("content", ""),
        role="user",
    )


@router.get(Routes.ROOT, summary=Summaries.MESSAGE_LIST)
async def list_messages(chatId: str, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.chat_history_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.CHAT_HISTORY_URI_NOT_SET)
    items = history.list_messages(history_uri=current_user.chat_history_uri, chat_id=chatId)
    return {Keys.CHAT_ID: chatId, Keys.ITEMS: items}


@router.get(Routes.MESSAGE_ID, summary=Summaries.MESSAGE_GET)
async def get_message(chatId: str, messageId: str, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.chat_history_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.CHAT_HISTORY_URI_NOT_SET)
    return history.get_message(history_uri=current_user.chat_history_uri, chat_id=chatId, message_id=messageId)


@router.put(Routes.MESSAGE_ID, summary=Summaries.MESSAGE_UPDATE)
async def update_message(
    chatId: str,
    messageId: str,
    payload: MessageUpdate = Body(default=None),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    # Stub: treat update as create of a new message for now
    if not current_user.chat_history_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.CHAT_HISTORY_URI_NOT_SET)
    body = payload.model_dump(exclude_none=True)
    return history.create_message(
        history_uri=current_user.chat_history_uri,
        chat_id=chatId,
        content=body.get("content", ""),
        role="user",
    )


@router.delete(Routes.MESSAGE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.MESSAGE_DELETE)
async def delete_message(chatId: str, messageId: str, current_user: User = Depends(get_current_user)) -> None:
    if not current_user.chat_history_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.CHAT_HISTORY_URI_NOT_SET)
    history.delete_message(history_uri=current_user.chat_history_uri, chat_id=chatId, message_id=messageId)
    return


