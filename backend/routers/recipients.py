from typing import Any, Dict
from fastapi import APIRouter, Body, status, Depends
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Fields
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.RECIPIENTS, tags=[Tags.RECIPIENTS], dependencies=[Depends(get_current_user)])


@router.get(Routes.ROOT, summary=Summaries.RECIPIENTS_LIST)
async def list_recipients() -> Dict[str, Any]:
    return {Keys.ITEMS: []}


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.RECIPIENT_CREATE)
async def create_recipient(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.RECIPIENT_CREATED, Keys.DATA: payload}


@router.get(Routes.ID, summary=Summaries.RECIPIENT_GET)
async def get_recipient(id: str) -> Dict[str, Any]:
    return {Fields.ID: id}


@router.put(Routes.ID, summary=Summaries.RECIPIENT_UPDATE)
async def update_recipient(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.RECIPIENT_UPDATED, Fields.ID: id, Keys.DATA: payload}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.RECIPIENT_DELETE)
async def delete_recipient(id: str) -> None:
    return


