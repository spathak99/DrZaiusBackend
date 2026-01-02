from typing import Dict, Any, List, Tuple, Optional
import logging
from backend.core.constants import Keys, Messages, Dlp, MimeTypes, Encoding, LogEvents
from backend.core.settings import get_settings

# Optional Google DLP imports at module top (safe when library not installed)
try:  # pragma: no cover
    from google.cloud import dlp_v2  # type: ignore
    from google.cloud.dlp_v2 import types  # type: ignore
except Exception:  # pragma: no cover
    dlp_v2 = None  # type: ignore
    types = None  # type: ignore


class DlpService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._logger = logging.getLogger(__name__)
        self._client = None
        self._parent: Optional[str] = None

        # Lazy/optional Google DLP wiring (dev-safe if lib/creds missing)
        if self._settings.enable_dlp and self._settings.gcp_project_id and dlp_v2 is not None:
            try:  # pragma: no cover
                self._client = dlp_v2.DlpServiceClient()
                location = self._settings.dlp_location or Dlp.DEFAULT_LOCATION
                self._parent = f"projects/{self._settings.gcp_project_id}/locations/{location}"
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
        Supports basic text and image flows. Falls back to no-op if DLP is disabled.
        """
        if not self._client or not self._parent or dlp_v2 is None:
            # No-op stub; DLP disabled or unavailable
            return content, []

        # Build inspect config
        info_type_names = list(self._settings.dlp_info_types or Dlp.DEFAULT_INFO_TYPES)
        # Strengthen SSN detection with a simple custom regex fallback (custom, not built-in)
        custom_info_types: List[Dict[str, Any]] = [
            {
                "info_type": {"name": "CUSTOM_SSN"},
                "regex": {"pattern": r"\b\d{3}-\d{2}-\d{4}\b"},
            }
        ]
        # Only pass built-in info types in the standard list; custom type is provided separately
        built_in_info_type_names = [t for t in info_type_names if t != "CUSTOM_SSN"]
        inspect_config: Dict[str, Any] = {
            "info_types": [{"name": t} for t in built_in_info_type_names],
            "min_likelihood": getattr(
                dlp_v2.Likelihood,
                (self._settings.dlp_min_likelihood or Dlp.DEFAULT_MIN_LIKELIHOOD).upper(),
                dlp_v2.Likelihood.POSSIBLE,
            ),
            "include_quote": True,
            "custom_info_types": custom_info_types,
        }

        # Branch by content type
        if mime_type and mime_type.startswith(MimeTypes.IMAGE_PREFIX):
            # Image redaction (black boxes over findings)
            if types is None:
                return content, []
            byte_item = {"type_": types.ByteContentItem.BytesType.IMAGE, "data": content}
            response = self._client.redact_image(
                request={
                    "parent": self._parent,
                    "inspect_config": inspect_config,
                    "byte_item": byte_item,
                    # Default behavior uses black boxes if no specific image_redaction_configs provided
                }
            )
            # redact_image doesn't return textual findings; return empty list
            return bytes(response.redacted_image), []

        # Default to text processing
        text_value = content.decode(Encoding.UTF8, errors="ignore")

        # First inspect to capture findings for caller UX
        inspect_resp = self._client.inspect_content(
            request={
                "parent": self._parent,
                "inspect_config": inspect_config,
                "item": {"value": text_value},
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
            "primitive_transformation": {
                "replace_with_info_type_config": {}
            }
        }
        # Apply transformation to all detected findings (built-in and custom) without enumerating names
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        **transformation,
                    }
                ]
            }
        }
        deid_resp = self._client.deidentify_content(
            request={
                "parent": self._parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": {"value": text_value},
            }
        )
        redacted_text = deid_resp.item.value if getattr(deid_resp, "item", None) else text_value
        return redacted_text.encode("utf-8"), findings


