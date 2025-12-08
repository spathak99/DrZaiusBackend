from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes
from backend.schemas import FileUpload, FileAccessGrant, FileAccessUpdate
from backend.services import FilesService
from backend.background.tasks import enqueue_embedding_job


router = APIRouter(prefix=Prefix.FILES, tags=[Tags.FILES])
service = FilesService()


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_UPLOAD)
async def upload_file(payload: FileUpload = Body(default=None)) -> Dict[str, Any]:
    return service.upload(payload.model_dump(exclude_none=True))


@router.get(Routes.ID, summary=Summaries.FILE_GET)
async def get_file(id: str) -> Dict[str, Any]:
    return service.get(id)


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_DELETE)
async def delete_file(id: str) -> None:
    service.delete(id)
    return


@router.post(Routes.FILE_ID + Routes.EMBEDDINGS, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_EMBEDDINGS_CREATE)
async def generate_file_embeddings(fileId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    job_id = enqueue_embedding_job("file", fileId, payload)
    return {"message": Messages.EMBEDDINGS_JOB_ENQUEUED, "fileId": fileId, "jobId": job_id}


@router.get(Routes.FILE_ID + Routes.EMBEDDINGS, summary=Summaries.FILE_EMBEDDINGS_GET)
async def get_file_embeddings(fileId: str) -> Dict[str, Any]:
    return {"fileId": fileId, "embeddings": []}


@router.get(Routes.ID + Routes.DOWNLOAD, summary=Summaries.FILE_DOWNLOAD)
async def download_file(id: str) -> Dict[str, Any]:
    return {"id": id, "download": "link"}


@router.get(Routes.FILE_ID + Routes.ACCESS, summary=Summaries.FILE_ACCESS_LIST)
async def list_file_access(fileId: str) -> Dict[str, Any]:
    return {"fileId": fileId, "items": service.list_access(fileId)}


@router.post(Routes.FILE_ID + Routes.ACCESS, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_ACCESS_GRANT)
async def grant_file_access(fileId: str, payload: FileAccessGrant = Body(default=None)) -> Dict[str, Any]:
    return service.grant_access(fileId, payload.model_dump())


@router.put(Routes.FILE_ID + Routes.ACCESS + Routes.CAREGIVER_ID, summary=Summaries.FILE_ACCESS_UPDATE)
async def update_file_access(
    fileId: str, caregiverId: str, payload: FileAccessUpdate = Body(default=None)
) -> Dict[str, Any]:
    return service.update_access(fileId, caregiverId, payload.model_dump())


@router.delete(Routes.FILE_ID + Routes.ACCESS + Routes.CAREGIVER_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_ACCESS_REVOKE)
async def revoke_file_access(fileId: str, caregiverId: str) -> None:
    service.revoke_access(fileId, caregiverId)
    return


