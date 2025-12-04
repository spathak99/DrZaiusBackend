from typing import Any, Dict
from fastapi import APIRouter
from backend.core.constants import Prefix, Tags, Summaries


router = APIRouter(prefix=Prefix.RECIPIENT_FILES, tags=[Tags.RECIPIENT_DATA])


@router.post("", status_code=201, summary=Summaries.FILE_UPLOAD)
async def upload_recipient_file(id: str) -> Dict[str, Any]:
    return {"message": "file uploaded", "recipientId": id}


@router.get("", summary=Summaries.FILE_DOWNLOAD)
async def list_recipient_files(id: str) -> Dict[str, Any]:
    return {"recipientId": id, "items": []}


@router.get("/{fileId}", summary=Summaries.FILE_DOWNLOAD)
async def get_recipient_file(id: str, fileId: str) -> Dict[str, Any]:
    return {"recipientId": id, "fileId": fileId}


@router.delete("/{fileId}", status_code=204, summary=Summaries.FILE_DELETE)
async def delete_recipient_file(id: str, fileId: str) -> None:
    return


