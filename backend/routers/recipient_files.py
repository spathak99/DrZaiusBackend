"""
Recipient files endpoints.

Upload behavior:
- Validates size (Upload.MAX_UPLOAD_MB) and MIME.
- If DLP is enabled and ready, redacts text/images in-memory before storing.
- Returns mimeType, redacted flag, and findings (for text) alongside data.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Errors, MimeTypes, Upload, LogEvents, Uploads
from backend.core.exceptions import AppError, to_http, DlpError, IngestionError, DocsError
from backend.db.database import get_db
from backend.db.models import User, RecipientCaregiverAccess
from backend.services import DocsService, IngestionService
from backend.services.dlp_service import DlpService
from backend.core.settings import get_settings
from backend.routers.deps import get_current_user, get_docs_service, get_ingestion_service, get_dlp_service
from backend.schemas.redaction import RedactUploadResponse
from backend.routers.helpers.access import assert_can_access_recipient


logger = logging.getLogger(__name__)
router = APIRouter(prefix=Prefix.RECIPIENT_FILES, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])

#

settings = get_settings()

def _assert_can_access_recipient(db: Session, recipient_id: str, current_user: User) -> None:
    # Backwards compatibility wrapper while refactoring callers progressively
    return assert_can_access_recipient(db, recipient_id, current_user)

@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_UPLOAD)
async def upload_recipient_file(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    docs: DocsService = Depends(get_docs_service),
    ingestion: IngestionService = Depends(get_ingestion_service),
    dlp: DlpService = Depends(get_dlp_service),
) -> Dict[str, Any]:
    """
    Upload a file for a recipient. If DLP is enabled and available:
    - Redacts text inputs and overlays black boxes on images.
    - Stores redacted bytes instead of the original.
    Response always includes mimeType and redacted flag; findings only for text.
    """
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    content = await file.read()
    size_bytes = len(content or b"")
    max_bytes = int(Upload.MAX_UPLOAD_MB) * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=Errors.PAYLOAD_TOO_LARGE)
    mime = file.content_type or MimeTypes.APPLICATION_OCTET_STREAM
    # Allow common text types in addition to images/PDF for pre-MVP
    if mime not in Uploads.ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=Errors.UNSUPPORTED_MEDIA_TYPE)
    # DLP redaction (feature-flagged and client-ready)
    redacted_bytes = content
    findings: List[Dict[str, Any]] = []
    attempted_redaction = False
    if settings.enable_dlp and dlp.is_ready():
		if mime.startswith(MimeTypes.IMAGE_PREFIX) or mime.startswith("text/") or mime in (MimeTypes.APPLICATION_JSON,):
			attempted_redaction = True
			try:
				redacted_bytes, findings = dlp.redact_content(
					content=content,
					mime_type=mime if mime.startswith(MimeTypes.IMAGE_PREFIX) else MimeTypes.TEXT_PLAIN,
				)
			except AppError as e:
				raise to_http(e)
			except Exception:
				# Fail open: proceed with original content if provider fails
				logger.warning("dlp_redact_failed", extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime})
				redacted_bytes, findings = content, []
    redacted_flag = redacted_bytes != content
    # If pipeline is enabled, enqueue to temp bucket + Pub/Sub instead of direct RAG
    if settings.enable_pipeline:
        if not user.gcp_project_id or not user.temp_bucket:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.MISSING_INGESTION_CONFIG)
		try:
			job = ingestion.enqueue_ingestion(
				user_id=str(user.id),
				gcp_project_id=user.gcp_project_id,
				temp_bucket=user.temp_bucket,
				file_name=file.filename or "upload",
				content_type=mime,
				content=redacted_bytes,
			)
		except AppError as e:
			raise to_http(e)
		except Exception:
			logger.error("ingestion_enqueue_failed", extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime})
			raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
        logger.info(
            LogEvents.FILE_REDACT_QUEUED if redacted_flag else LogEvents.FILE_QUEUED,
            extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime, Keys.SIZE_BYTES: size_bytes, Keys.REDACTED: redacted_flag},
        )
        data = {**job, Keys.MIME_TYPE: mime, Keys.REDACTED: redacted_flag}
        # Only include findings for text-like content
        if findings:
            data[Keys.FINDINGS] = findings
        return {
            Keys.MESSAGE: Messages.FILE_QUEUED,
            Keys.RECIPIENT_ID: id,
            Keys.MIME_TYPE: mime,
            Keys.REDACTED: redacted_flag,
            **({Keys.FINDINGS: findings} if findings else {}),
            Keys.DATA: data,
        }
    # Default: direct ingestion to RAG
	try:
		created = docs.upload_doc(corpus_uri=user.corpus_uri, file_name=file.filename, content_type=mime, content=redacted_bytes)
	except AppError as e:
		raise to_http(e)
	except Exception:
		logger.error("docs_upload_failed", extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime})
		raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
    logger.info(
        LogEvents.FILE_REDACT_UPLOADED if redacted_flag else LogEvents.FILE_UPLOADED,
        extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime, Keys.SIZE_BYTES: size_bytes, Keys.REDACTED: redacted_flag},
    )
    data = {**created, Keys.MIME_TYPE: mime, Keys.REDACTED: redacted_flag}
    if findings:
        data[Keys.FINDINGS] = findings
    return {
        Keys.MESSAGE: Messages.FILE_UPLOADED,
        Keys.RECIPIENT_ID: id,
        Keys.MIME_TYPE: mime,
        Keys.REDACTED: redacted_flag,
        **({Keys.FINDINGS: findings} if findings else {}),
        Keys.DATA: data,
    }


@router.get(Routes.ROOT, summary=Summaries.RECIPIENT_FILES_LIST)
async def list_recipient_files(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    docs: DocsService = Depends(get_docs_service),
) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    try:
        items = docs.list_docs(corpus_uri=user.corpus_uri)
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
    return {Keys.RECIPIENT_ID: id, Keys.ITEMS: items}


@router.get(Routes.FILE_ID, summary=Summaries.FILE_DOWNLOAD)
async def get_recipient_file(
    id: str,
    fileId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    docs: DocsService = Depends(get_docs_service),
) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    try:
        doc = docs.get_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
    return {Keys.RECIPIENT_ID: id, Keys.FILE_ID: fileId, Keys.DATA: doc}


@router.delete(Routes.FILE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_DELETE)
async def delete_recipient_file(
    id: str,
    fileId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    docs: DocsService = Depends(get_docs_service),
) -> None:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    try:
        docs.delete_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
    return


@router.post("/redact-upload", status_code=status.HTTP_201_CREATED, summary="Redact sensitive data then upload", response_model=RedactUploadResponse)
async def redact_and_upload_recipient_file(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dlp: DlpService = Depends(get_dlp_service),
    ingestion: IngestionService = Depends(get_ingestion_service),
    docs: DocsService = Depends(get_docs_service),
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
    size_bytes = len(raw or b"")
    max_bytes = int(Upload.MAX_UPLOAD_MB) * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=Errors.PAYLOAD_TOO_LARGE)
    mime = file.content_type or MimeTypes.APPLICATION_OCTET_STREAM
    if mime not in Uploads.ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=Errors.UNSUPPORTED_MEDIA_TYPE)
	try:
		redacted_bytes, findings = dlp.redact_content(content=raw, mime_type=mime)
	except AppError as e:
		raise to_http(e)
	except Exception:
		logger.warning("dlp_redact_failed", extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime})
		redacted_bytes, findings = raw, []
    redacted_types: List[str] = sorted({str((f or {}).get("info_type", "")).strip() for f in findings if (f or {}).get("info_type")})
    # Ingestion path
    if settings.enable_pipeline:
        if not user.gcp_project_id or not user.temp_bucket:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.MISSING_INGESTION_CONFIG)
		try:
			job = ingestion.enqueue_ingestion(
				user_id=str(user.id),
				gcp_project_id=user.gcp_project_id,
				temp_bucket=user.temp_bucket,
				file_name=file.filename or "upload",
				content_type=mime,
				content=redacted_bytes,
			)
		except AppError as e:
			raise to_http(e)
		except Exception:
			logger.error("ingestion_enqueue_failed", extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime})
			raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
        logger.info(
            LogEvents.FILE_REDACT_QUEUED,
            extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime, Keys.SIZE_BYTES: size_bytes, Keys.REDACTED_TYPES_COUNT: len(redacted_types)},
        )
        return {
            Keys.MESSAGE: Messages.FILE_QUEUED,
            Keys.RECIPIENT_ID: id,
            Keys.MIME_TYPE: mime,
            Keys.REDACTED: redacted_bytes != raw,
            Keys.FINDINGS: findings,
            Keys.DATA: {**job, Keys.REDACTED_TYPES: redacted_types},
        }
    # Direct upload to corpus
	try:
		created = docs.upload_doc(
			corpus_uri=user.corpus_uri,
			file_name=file.filename or "upload",
			content_type=mime,
			content=redacted_bytes,
		)
	except AppError as e:
		raise to_http(e)
	except Exception:
		logger.error("docs_upload_failed", extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime})
		raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=Errors.INTERNAL_ERROR)
    logger.info(LogEvents.FILE_REDACT_UPLOADED, extra={Keys.RECIPIENT_ID: id, Keys.MIME_TYPE: mime, Keys.SIZE_BYTES: size_bytes, Keys.REDACTED_TYPES_COUNT: len(redacted_types)})
    return {
        Keys.MESSAGE: Messages.FILE_UPLOADED,
        Keys.RECIPIENT_ID: id,
        Keys.MIME_TYPE: mime,
        Keys.REDACTED: redacted_bytes != raw,
        Keys.FINDINGS: findings,
        Keys.DATA: {**created, Keys.REDACTED_TYPES: redacted_types},
    }


