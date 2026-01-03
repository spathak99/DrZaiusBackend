"""
Redaction endpoints.

Provides:
- POST /redaction/test: quick inline text redaction check
- GET /redaction/status: feature/config readiness
- POST /redaction/file: redact uploaded text or image
"""
from __future__ import annotations

from fastapi import APIRouter, Body, Depends, status, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
import io
import base64

from backend.core.constants import Prefix, Tags, Summaries, MimeTypes, Encoding, Keys
from backend.services.dlp_service import DlpService
from backend.routers.deps import get_current_user, get_dlp_service
from backend.db.models import User
from backend.schemas.redaction import RedactionTestRequest, RedactionTestResponse, RedactionStatusResponse, RedactionTextFileResponse


router = APIRouter(prefix=Prefix.REDACTION, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])


@router.post("/test", status_code=status.HTTP_200_OK, summary=Summaries.REDACTION_TEST, response_model=RedactionTestResponse)
async def redaction_test(
	payload: RedactionTestRequest = Body(...),
	dlp: DlpService = Depends(get_dlp_service),
	current_user: User = Depends(get_current_user),
) -> RedactionTestResponse:
	"""
	Perform a quick DLP redaction against inline text.

	Returns input/output lengths, findings, and the redacted text.
	"""
	redacted, findings = dlp.redact_content(content=payload.text.encode(Encoding.UTF8), mime_type=MimeTypes.TEXT_PLAIN)
	return {
		"input_len": len(payload.text.encode(Encoding.UTF8)),
		"output_len": len(redacted),
		"findings": findings,
		"redactedText": redacted.decode(Encoding.UTF8, errors="ignore"),
	}

@router.get("/status", status_code=status.HTTP_200_OK, response_model=RedactionStatusResponse)
async def redaction_status(
	dlp: DlpService = Depends(get_dlp_service),
	current_user: User = Depends(get_current_user),
) -> RedactionStatusResponse:
	"""
	Report whether DLP is enabled and the client is ready to serve requests.
	"""
	from backend.core.settings import get_settings
	settings = get_settings()
	return {
		Keys.ENABLE_DLP: settings.enable_dlp,
		Keys.PROJECT_ID: settings.gcp_project_id,
		Keys.LOCATION: settings.dlp_location,
		Keys.CLIENT_READY: dlp.is_ready(),
	}


@router.post("/file", status_code=status.HTTP_200_OK, summary="Redact an uploaded file (text or image)")
async def redact_file(
	file: UploadFile = File(...),
	asBase64: bool = Query(default=False, description="When true for image/*, return JSON with base64 instead of streaming"),
	dlp: DlpService = Depends(get_dlp_service),
	current_user: User = Depends(get_current_user),
):
	"""
	Redact an uploaded file.
	- Text: returns JSON with redactedText and findings
	- Image: returns redacted bytes as a streamed response
	"""
	# Read file bytes
	data = await file.read()
	content_type = file.content_type or ""

	# Image flow: return redacted bytes, no findings
	if content_type.startswith(MimeTypes.IMAGE_PREFIX):
		redacted_bytes, _ = dlp.redact_content(content=data, mime_type=content_type)
		if asBase64:
			b64 = base64.b64encode(redacted_bytes).decode("ascii")
			return {Keys.IMAGE_BASE64: b64, Keys.MIME_TYPE: content_type or "image/png"}
		return StreamingResponse(io.BytesIO(redacted_bytes), media_type=content_type or "image/png")

	# Text flow: return JSON with redactedText and findings
	if content_type.startswith("text/") or content_type in ("application/json",):
		redacted_bytes, findings = dlp.redact_content(content=data, mime_type=MimeTypes.TEXT_PLAIN)
		return RedactionTextFileResponse(
			redactedText=redacted_bytes.decode(Encoding.UTF8, errors="ignore"),
			findings=findings,
		)

	# Unsupported
	raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Unsupported content type: {content_type}")

