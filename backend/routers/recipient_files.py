from typing import Any, Dict, List
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Errors
from backend.db.database import get_db
from backend.db.models import User, RecipientCaregiverAccess
from backend.services import DocsService, IngestionService
from backend.services.dlp_service import DlpService
from backend.core.settings import get_settings
from backend.routers.deps import get_current_user
from backend.schemas.redaction import RedactUploadResponse


router = APIRouter(prefix=Prefix.RECIPIENT_FILES, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])
docs = DocsService()
ingestion = IngestionService()
dlp = DlpService()
settings = get_settings()

def _assert_can_access_recipient(db: Session, recipient_id: str, current_user: User) -> None:
    # Allow self
    if str(current_user.id) == recipient_id:
        return
    # Otherwise require caregiver access row
    allowed = db.scalar(
        select(RecipientCaregiverAccess).where(
            RecipientCaregiverAccess.recipient_id == recipient_id,
            RecipientCaregiverAccess.caregiver_id == current_user.id,
        )
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)

@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_UPLOAD)
async def upload_recipient_file(
    id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    content = await file.read()
    # If pipeline is enabled, enqueue to temp bucket + Pub/Sub instead of direct RAG
    if settings.enable_pipeline:
        if not user.gcp_project_id or not user.temp_bucket:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.MISSING_INGESTION_CONFIG)
        job = ingestion.enqueue_ingestion(
            user_id=str(user.id),
            gcp_project_id=user.gcp_project_id,
            temp_bucket=user.temp_bucket,
            file_name=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            content=content,
        )
        return {Keys.MESSAGE: Messages.FILE_QUEUED, Keys.RECIPIENT_ID: id, Keys.DATA: job}
    # Default: direct ingestion to RAG
    created = docs.upload_doc(corpus_uri=user.corpus_uri, file_name=file.filename, content_type=file.content_type, content=content)
    return {Keys.MESSAGE: Messages.FILE_UPLOADED, Keys.RECIPIENT_ID: id, Keys.DATA: created}


@router.get(Routes.ROOT, summary=Summaries.RECIPIENT_FILES_LIST)
async def list_recipient_files(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    items = docs.list_docs(corpus_uri=user.corpus_uri)
    return {Keys.RECIPIENT_ID: id, Keys.ITEMS: items}


@router.get(Routes.FILE_ID, summary=Summaries.FILE_DOWNLOAD)
async def get_recipient_file(id: str, fileId: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    doc = docs.get_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    return {Keys.RECIPIENT_ID: id, Keys.FILE_ID: fileId, Keys.DATA: doc}


@router.delete(Routes.FILE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_DELETE)
async def delete_recipient_file(id: str, fileId: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    docs.delete_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    return


@router.post("/redact-upload", status_code=status.HTTP_201_CREATED, summary="Redact sensitive data then upload", response_model=RedactUploadResponse)
async def redact_and_upload_recipient_file(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    MVP endpoint:
    - Redacts content via DlpService
    - Enqueues ingestion if pipeline enabled, otherwise uploads directly to corpus
    - Returns findings summary (types redacted) and job/document info
    """
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    raw = await file.read()
    redacted_bytes, findings = dlp.redact_content(content=raw, mime_type=file.content_type or "application/octet-stream")
    redacted_types: List[str] = sorted({str((f or {}).get("info_type", "")).strip() for f in findings if (f or {}).get("info_type")})
    # Ingestion path
    if settings.enable_pipeline:
        if not user.gcp_project_id or not user.temp_bucket:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.MISSING_INGESTION_CONFIG)
        job = ingestion.enqueue_ingestion(
            user_id=str(user.id),
            gcp_project_id=user.gcp_project_id,
            temp_bucket=user.temp_bucket,
            file_name=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            content=redacted_bytes,
        )
        return {
            Keys.MESSAGE: Messages.FILE_QUEUED,
            Keys.RECIPIENT_ID: id,
            Keys.DATA: {**job, "redacted_types": redacted_types, "findings": findings},
        }
    # Direct upload to corpus
    created = docs.upload_doc(
        corpus_uri=user.corpus_uri,
        file_name=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        content=redacted_bytes,
    )
    return {
        Keys.MESSAGE: Messages.FILE_UPLOADED,
        Keys.RECIPIENT_ID: id,
        Keys.DATA: {**created, "redacted_types": redacted_types, "findings": findings},
    }


