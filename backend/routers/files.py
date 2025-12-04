from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags
from backend.schemas import FileUpload, FileAccessGrant, FileAccessUpdate
from backend.services import FilesService
from backend.background.tasks import enqueue_embedding_job


router = APIRouter(prefix=Prefix.FILES, tags=[Tags.FILES])
service = FilesService()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Upload a file")
async def upload_file(payload: FileUpload = Body(default=None)) -> Dict[str, Any]:
    return service.upload(payload.model_dump(exclude_none=True))


@router.get("/{id}", summary="Get a specific file by ID")
async def get_file(id: str) -> Dict[str, Any]:
    return service.get(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a file by ID")
async def delete_file(id: str) -> None:
    service.delete(id)
    return


@router.post(
    "/{fileId}/embeddings",
    status_code=status.HTTP_201_CREATED,
    summary="Generate embeddings for a file",
)
async def generate_file_embeddings(fileId: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    job_id = enqueue_embedding_job("file", fileId, payload)
    return {"message": "embeddings job enqueued", "fileId": fileId, "jobId": job_id}


@router.get("/{fileId}/embeddings", summary="Get embeddings for a file")
async def get_file_embeddings(fileId: str) -> Dict[str, Any]:
    return {"fileId": fileId, "embeddings": []}


@router.get("/{id}/download", summary="Download file by ID")
async def download_file(id: str) -> Dict[str, Any]:
    return {"id": id, "download": "link"}


@router.get("/{fileId}/access", summary="List file access control entries")
async def list_file_access(fileId: str) -> Dict[str, Any]:
    return {"fileId": fileId, "items": service.list_access(fileId)}


@router.post("/{fileId}/access", status_code=status.HTTP_201_CREATED, summary="Grant access to caregiver")
async def grant_file_access(fileId: str, payload: FileAccessGrant = Body(default=None)) -> Dict[str, Any]:
    return service.grant_access(fileId, payload.model_dump())


@router.put("/{fileId}/access/{caregiverId}", summary="Update caregiver access level for file")
async def update_file_access(
    fileId: str, caregiverId: str, payload: FileAccessUpdate = Body(default=None)
) -> Dict[str, Any]:
    return service.update_access(fileId, caregiverId, payload.model_dump())


@router.delete(
    "/{fileId}/access/{caregiverId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke caregiver access to file",
)
async def revoke_file_access(fileId: str, caregiverId: str) -> None:
    service.revoke_access(fileId, caregiverId)
    return


