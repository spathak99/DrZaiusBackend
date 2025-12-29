import json
import logging
import urllib.request
from typing import Optional

from backend.core.settings import get_settings
from backend.core.constants import Email, MimeTypes, Urls

logger = logging.getLogger(__name__)


def send_invite_email(to_email: str, accept_url: Optional[str]) -> None:
    """
    Send an invitation email with an accept link.
    If SENDGRID_API_KEY is not set, logs the message instead.
    """
    settings = get_settings()
    subject = Email.SUBJECT_INVITE
    text_body = f"You've been invited. Accept here: {accept_url or '(link unavailable)'}"
    html_body = f"<p>You've been invited.</p><p><a href=\"{accept_url or '#'}\">Tap to accept</a></p>"

    if not settings.sendgrid_api_key:
        logger.info("[email] To: %s | %s", to_email, text_body)
        return

    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.email_from},
        "subject": subject,
        "content": [
            {"type": MimeTypes.TEXT_PLAIN, "value": text_body},
            {"type": MimeTypes.TEXT_HTML, "value": html_body},
        ],
    }
    req = urllib.request.Request(
        Urls.SENDGRID_API_SEND,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.sendgrid_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
    except Exception as e:
        logger.warning("SendGrid error: %s", e)
        # Fallback to log so dev can still test
        logger.info("[email-fallback] To: %s | %s", to_email, text_body)


