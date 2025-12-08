from typing import Any, Dict
from fastapi import APIRouter, Body, Path, status
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes
from backend.schemas import ChatCreate, ChatUpdate
from backend.services import ChatsService
from backend.background.tasks import enqueue_embedding_job


router = APIRouter(prefix=Prefix.CHATS, tags=[Tags.CHATS])
service = ChatsService()


@router.get(Routes.ROOT, summary=Summaries.LIST_CHATS)
async def list_chats() -> Dict[str, Any]:
    return {"items": service.list_chats()}


@router.get(Routes.ID, summary=Summaries.GET_CHAT)
async def get_chat(id: str = Path(...)) -> Dict[str, Any]:
    return service.get_chat(id)


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.CREATE_CHAT)
async def create_chat(payload: ChatCreate = Body(default=None)) -> Dict[str, Any]:
    return service.create_chat(payload.model_dump())


@router.put(Routes.ID, summary=Summaries.UPDATE_CHAT)
async def update_chat(id: str, payload: ChatUpdate = Body(default=None)) -> Dict[str, Any]:
    return service.update_chat(id, payload.model_dump(exclude_none=True))


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.DELETE_CHAT)
async def delete_chat(id: str) -> None:
    service.delete_chat(id)
    return


@router.post(Routes.CHAT_ID + Routes.EMBEDDINGS, status_code=status.HTTP_201_CREATED, summary=Summaries.CHAT_EMBEDDINGS_CREATE)
async def generate_chat_embeddings(chatId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    job_id = enqueue_embedding_job("chat", chatId, payload)
    return {"message": Messages.EMBEDDINGS_JOB_ENQUEUED, "chatId": chatId, "jobId": job_id}


@router.get(Routes.CHAT_ID + Routes.EMBEDDINGS, summary=Summaries.CHAT_EMBEDDINGS_GET)
async def get_chat_embeddings(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "embeddings": []}


