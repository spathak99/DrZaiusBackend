from typing import Any, Dict
from fastapi import APIRouter, status, Depends
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.RECIPIENT_FILES, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_UPLOAD)
async def upload_recipient_file(id: str) -> Dict[str, Any]:
    return {"message": Messages.FILE_UPLOADED, "recipientId": id}


@router.get(Routes.ROOT, summary=Summaries.RECIPIENT_FILES_LIST)
async def list_recipient_files(id: str) -> Dict[str, Any]:
    return {"recipientId": id, "items": []}


@router.get(Routes.FILE_ID, summary=Summaries.FILE_DOWNLOAD)
async def get_recipient_file(id: str, fileId: str) -> Dict[str, Any]:
    return {"recipientId": id, "fileId": fileId}


@router.delete(Routes.FILE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_DELETE)
async def delete_recipient_file(id: str, fileId: str) -> None:
    return


