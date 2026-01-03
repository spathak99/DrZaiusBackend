"""
Backend DLP service integration.

Provides in-memory redaction for text and images via Google Cloud DLP,
with safe fallbacks when disabled or unavailable.
"""
from typing import Dict, Any, List, Tuple, Optional
import logging
from backend.core.constants import Keys, Messages, Dlp, MimeTypes, Encoding, LogEvents, DlpReq
from backend.core.settings import get_settings

# Optional Google DLP imports at module top (safe when library not installed)
try:  # pragma: no cover
    from google.cloud import dlp_v2  # type: ignore
    from google.cloud.dlp_v2 import types  # type: ignore
except Exception:  # pragma: no cover
    dlp_v2 = None  # type: ignore
    types = None  # type: ignore


class DlpService:
    """
    Thin wrapper around Google Cloud DLP for in-memory content redaction.
    - Resilient when DLP is disabled or unavailable: returns original content.
    - Supports text (inspect + deidentify) and image (redact_image) flows.
    - Findings are returned for text to support UX surfacing.
    """
    def __init__(self) -> None:
        """
        Initialize the service and lazily wire the Google DLP client if enabled.
        Safe in dev environments without GCP credentials or library installed.
        """
        self._settings = get_settings()
        self._logger = logging.getLogger(__name__)
        self._client = None
        self._parent: Optional[str] = None

        # Lazy/optional Google DLP wiring (dev-safe if lib/creds missing)
        if self._settings.enable_dlp and self._settings.gcp_project_id and dlp_v2 is not None:
            try:  # pragma: no cover
                self._client = dlp_v2.DlpServiceClient()
                location = self._settings.dlp_location or Dlp.DEFAULT_LOCATION
                self._parent = Dlp.PARENT_PATH_TEMPLATE.format(project_id=self._settings.gcp_project_id, location=location)
                self._logger.info("%s (location=%s)", LogEvents.DLP_ENABLED, location)
            except Exception as exc:
                # Fall back silently to stub behavior; log at WARN for awareness
                self._client = None
                self._parent = None
                self._logger.warning("%s: %s", LogEvents.DLP_CLIENT_INIT_ERROR, exc)
        else:
            self._logger.info("%s: enable_dlp=%s, project_id set=%s", LogEvents.DLP_DISABLED, self._settings.enable_dlp, bool(self._settings.gcp_project_id))

    def redact(self, *, bucket: str, object_name: str) -> Dict[str, Any]:
        """
        For future GCS-object redaction flows. Currently returns a placeholder
        response indicating redaction would be scheduled.
        """
        return {Keys.BUCKET: bucket, Keys.OBJECT: object_name, Keys.STATUS: Messages.DLP_REDACTION_SCHEDULED}

    def is_ready(self) -> bool:
        """
        Returns True when DLP client is initialized and a valid parent path is set.
        """
        return self._client is not None and self._parent is not None

    def redact_content(self, *, content: bytes, mime_type: Optional[str] = None) -> Tuple[bytes, List[Dict[str, Any]]]:
        """
        Redact in-memory content using Google Cloud DLP when enabled and available.
        - Text: returns (redacted_bytes, findings)
        - Images: returns (redacted_bytes, [])
        Falls back to no-op (content, []) if DLP is disabled/unavailable.
        """
        if not self._client or not self._parent or dlp_v2 is None:
            # No-op stub; DLP disabled or unavailable
            return content, []

        # Build inspect config
        info_type_names = list(self._settings.dlp_info_types or Dlp.DEFAULT_INFO_TYPES)
        # Normalize info type names to provider's expected uppercase format
        info_type_names = [str(t or "").strip().upper() for t in info_type_names if str(t or "").strip()]
        # Strengthen SSN detection with a simple custom regex fallback (custom, not built-in)
        custom_info_types: List[Dict[str, Any]] = [
            {
                "info_type": {"name": Dlp.CUSTOM_SSN_NAME},
                "regex": {"pattern": Dlp.REGEX_SSN},
            }
        ]
        # Only pass built-in info types in the standard list; custom type is provided separately
        built_in_info_type_names = [t for t in info_type_names if t != Dlp.CUSTOM_SSN_NAME]
        inspect_config: Dict[str, Any] = {
            DlpReq.INFO_TYPES: [{"name": t} for t in built_in_info_type_names],
            DlpReq.MIN_LIKELIHOOD: getattr(
                dlp_v2.Likelihood,
                (self._settings.dlp_min_likelihood or Dlp.DEFAULT_MIN_LIKELIHOOD).upper(),
                dlp_v2.Likelihood.POSSIBLE,
            ),
            DlpReq.INCLUDE_QUOTE: True,
            DlpReq.CUSTOM_INFO_TYPES: custom_info_types,
        }

        # Branch by content type
        if mime_type and mime_type.startswith(MimeTypes.IMAGE_PREFIX):
            # Image redaction (black boxes over findings)
            if types is None:
                return content, []
            byte_item = {DlpReq.TYPE_: types.ByteContentItem.BytesType.IMAGE, DlpReq.DATA: content}
            try:
                response = self._client.redact_image(
                    request={
                        DlpReq.PARENT: self._parent,
                        DlpReq.INSPECT_CONFIG: inspect_config,
                        DlpReq.BYTE_ITEM: byte_item,
                        # Default behavior uses black boxes if no specific image_redaction_configs provided
                    }
                )
                # redact_image doesn't return textual findings; return empty list
                return bytes(response.redacted_image), []
            except Exception as exc:
                self._logger.warning("%s: %s", LogEvents.DLP_REDACT_IMAGE_FAILED, exc)
                return content, []

        # Default to text processing
        text_value = content.decode(Encoding.UTF8, errors="ignore")
        # Safety cap large inputs
        if len(text_value.encode(Encoding.UTF8)) > Dlp.MAX_TEXT_BYTES:
            self._logger.warning("dlp_text_truncated: sizeBytes=%s cap=%s", len(text_value.encode(Encoding.UTF8)), Dlp.MAX_TEXT_BYTES)
            # Truncate by bytes to avoid splitting multi-byte mid-character
            text_bytes = text_value.encode(Encoding.UTF8)[: Dlp.MAX_TEXT_BYTES]
            text_value = text_bytes.decode(Encoding.UTF8, errors="ignore")

        # First inspect to capture findings for caller UX
        inspect_resp = self._client.inspect_content(
            request={
                DlpReq.PARENT: self._parent,
                DlpReq.INSPECT_CONFIG: inspect_config,
                DlpReq.ITEM: {DlpReq.VALUE: text_value},
            }
        )
        findings: List[Dict[str, Any]] = []
        for f in inspect_resp.result.findings or []:
            try:
                info_type = f.info_type.name if getattr(f, "info_type", None) else None
                quote = getattr(f, "quote", None)
                if info_type:
                    findings.append({"info_type": info_type, "quote": quote})
            except Exception:
                # Be resilient to provider changes
                continue

        # Then deidentify to redact (mask or replace with [INFO_TYPE])
        # Using replace-with-info-type to preserve readability by default
        transformation = {
            DlpReq.PRIMITIVE_TRANSFORMATION: {
                DlpReq.REPLACE_WITH_INFO_TYPE_CONFIG: {}
            }
        }
        # Apply transformation to all detected findings (built-in and custom) without enumerating names
        deidentify_config = {
            DlpReq.INFO_TYPE_TRANSFORMATIONS: {
                DlpReq.TRANSFORMATIONS: [
                    {
                        **transformation,
                    }
                ]
            }
        }
        deid_resp = self._client.deidentify_content(
            request={
                DlpReq.PARENT: self._parent,
                DlpReq.DEIDENTIFY_CONFIG: deidentify_config,
                DlpReq.INSPECT_CONFIG: inspect_config,
                DlpReq.ITEM: {DlpReq.VALUE: text_value},
            }
        )
        redacted_text = deid_resp.item.value if getattr(deid_resp, "item", None) else text_value
        return redacted_text.encode(Encoding.UTF8), findings


