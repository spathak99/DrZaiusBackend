from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from backend.core.constants import API_TITLE, Cors
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


