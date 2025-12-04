from typing import Any, Dict
from fastapi import APIRouter, Body, Path, status
from backend.core.constants import Prefix, Tags
from backend.schemas import ChatCreate, ChatUpdate
from backend.services import ChatsService
from backend.background.tasks import enqueue_embedding_job


router = APIRouter(prefix=Prefix.CHATS, tags=[Tags.CHATS])
service = ChatsService()


@router.get("", summary="Get a list of all chats")
async def list_chats() -> Dict[str, Any]:
    return {"items": service.list_chats()}


@router.get("/{id}", summary="Get a specific chat by ID")
async def get_chat(id: str = Path(...)) -> Dict[str, Any]:
    return service.get_chat(id)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new chat")
async def create_chat(payload: ChatCreate = Body(default=None)) -> Dict[str, Any]:
    return service.create_chat(payload.model_dump())


@router.put("/{id}", summary="Update a chat by ID")
async def update_chat(id: str, payload: ChatUpdate = Body(default=None)) -> Dict[str, Any]:
    return service.update_chat(id, payload.model_dump(exclude_none=True))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a chat by ID")
async def delete_chat(id: str) -> None:
    service.delete_chat(id)
    return


@router.post(
    "/{chatId}/embeddings",
    status_code=status.HTTP_201_CREATED,
    summary="Generate embeddings for a chat",
)
async def generate_chat_embeddings(chatId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    job_id = enqueue_embedding_job("chat", chatId, payload)
    return {"message": "embeddings job enqueued", "chatId": chatId, "jobId": job_id}


@router.get("/{chatId}/embeddings", summary="Get embeddings for a chat")
async def get_chat_embeddings(chatId: str) -> Dict[str, Any]:
    return {"chatId": chatId, "embeddings": []}


