from __future__ import annotations

from fastapi import APIRouter, Body, Depends, status

from backend.core.constants import Prefix, Tags, Summaries, MimeTypes, Encoding, Keys
from backend.services.dlp_service import DlpService
from backend.routers.deps import get_current_user, get_dlp_service
from backend.db.models import User
from backend.schemas.redaction import RedactionTestRequest, RedactionTestResponse, RedactionStatusResponse


router = APIRouter(prefix=Prefix.REDACTION, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])


@router.post("/test", status_code=status.HTTP_200_OK, summary=Summaries.REDACTION_TEST, response_model=RedactionTestResponse)
async def redaction_test(
	payload: RedactionTestRequest = Body(...),
	dlp: DlpService = Depends(get_dlp_service),
	current_user: User = Depends(get_current_user),
) -> RedactionTestResponse:
	redacted, findings = dlp.redact_content(content=payload.text.encode(Encoding.UTF8), mime_type=MimeTypes.TEXT_PLAIN)
	return {"input_len": len(payload.text.encode(Encoding.UTF8)), "output_len": len(redacted), "findings": findings}

@router.get("/status", status_code=status.HTTP_200_OK, response_model=RedactionStatusResponse)
async def redaction_status(
	dlp: DlpService = Depends(get_dlp_service),
	current_user: User = Depends(get_current_user),
) -> RedactionStatusResponse:
	from backend.core.settings import get_settings
	settings = get_settings()
	return {
		"enableDlp": settings.enable_dlp,
		"projectId": settings.gcp_project_id,
		"location": settings.dlp_location,
		"clientReady": dlp.is_ready(),
	}

