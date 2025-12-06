from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import Timestamped


class ChatParticipantAdd(BaseModel):
    user_id: UUID


class ChatParticipantResponse(Timestamped):
    id: UUID
    chat_id: UUID
    user_id: UUID


