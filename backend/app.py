from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.constants import API_TITLE, Cors
from backend.core.settings import get_settings
from backend.routers import (
    auth,
    users,
    chats,
    user_chats,
    messages,
    participants,
    recipients,
    caregivers,
    recipient_files,
    access,
    files,
    security,
    compliance,
    ops,
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
app.include_router(chats.router)
app.include_router(user_chats.router)
app.include_router(messages.router)
app.include_router(participants.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipients.router)
app.include_router(caregivers.router)
app.include_router(recipient_files.router)
app.include_router(access.recipient_access_router)
app.include_router(access.caregiver_recipients_router)
app.include_router(access.caregiver_invitations_router)
app.include_router(access.recipient_invitations_router)
app.include_router(files.router)
app.include_router(security.keys_router)
app.include_router(security.policies_router)
app.include_router(compliance.router)
app.include_router(ops.router)


@app.on_event("startup")
def maybe_create_tables() -> None:
    settings = get_settings()
    if settings.auto_create_db:
        # Dev-only convenience to bootstrap tables without Alembic
        from backend.db import Base, engine

        Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)


