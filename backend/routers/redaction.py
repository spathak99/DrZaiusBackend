from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, status

from backend.core.constants import Prefix, Tags, Summaries, Keys
from backend.services.dlp_service import DlpService
from backend.routers.deps import get_current_user
from backend.db.models import User


router = APIRouter(prefix=Prefix.REDACTION, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])
dlp = DlpService()


@router.post("/test", status_code=status.HTTP_200_OK, summary=Summaries.REDACTION_TEST)
async def redaction_test(
	text: str = Body(..., embed=True),
	current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
	redacted, findings = dlp.redact_content(content=text.encode("utf-8"), mime_type="text/plain")
	return {Keys.DATA: {"input_len": len(text.encode("utf-8")), "output_len": len(redacted), "findings": findings}}


