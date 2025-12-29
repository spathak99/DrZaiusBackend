from fastapi import FastAPI, Request, status
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from backend.core.constants import API_TITLE, Cors, Keys, Errors, Headers
from backend.core.settings import get_settings
from backend.routers import (
    auth,
    users,
    # chats,
    # user_chats,
    messages,
    # participants,
    recipients,
    caregivers,
    recipient_files,
    access,
    # files,
    security,
    compliance,
    ops,
    groups,
    rag,
)


app = FastAPI(title=API_TITLE)
logger = logging.getLogger(__name__)

# CORS
_settings = get_settings()
_cors_origins = _settings.cors_origins or Cors.DEFAULT_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=Cors.ALLOW_METHODS_ALL,
    allow_headers=Cors.ALLOW_HEADERS_ALL,
)
if not _settings.invite_signing_secret:
    logger.warning("INVITE_SIGNING_SECRET is not set; invite token verification may fail.")
if not _settings.email_from:
    logger.warning("EMAIL_FROM is not set; email sender will default to placeholder.")

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(Headers.REQUEST_ID) or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[Headers.REQUEST_ID] = request_id
        return response

app.add_middleware(RequestIdMiddleware)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = {Keys.MESSAGE: Errors.INVALID_PAYLOAD, "details": exc.errors(), Keys.REQUEST_ID: getattr(request.state, "request_id", None)}
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=body)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled exception", extra={"requestId": getattr(request.state, "request_id", None)})
    body = {Keys.MESSAGE: Errors.INTERNAL_ERROR, Keys.REQUEST_ID: getattr(request.state, "request_id", None)}
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)

# Register routers
# app.include_router(chats.router)
# app.include_router(user_chats.router)
app.include_router(messages.router)
# app.include_router(participants.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipients.router)
app.include_router(caregivers.router)
app.include_router(recipient_files.router)
app.include_router(access.recipient_access_router)
app.include_router(access.caregiver_recipients_router)
app.include_router(access.caregiver_invitations_router)
app.include_router(access.recipient_invitations_router)
app.include_router(access.public_invites_router)
# app.include_router(files.router)
app.include_router(security.keys_router)
app.include_router(security.policies_router)
app.include_router(compliance.router)
app.include_router(ops.router)
app.include_router(groups.router)
app.include_router(rag.router)


@app.on_event("startup")
def maybe_create_tables() -> None:
    settings = get_settings()
    if settings.auto_create_db:
        # Dev-only convenience to bootstrap tables without Alembic
        from backend.db import Base, engine

        Base.metadata.create_all(bind=engine)


# OpenAPI: add global bearer auth
def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=API_TITLE, version="1.0.0", routes=app.routes)
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["bearerAuth"] = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = _custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)


