"""Chat history service: mock read/write against a per-user history URI."""
from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4
from time import time

from backend.core.constants import Keys, ChatKeys, Messages, ChatRoles


class ChatHistoryService:
    """
    Stubbed chat history stored against a per-user history URI (e.g., GCS path).
    """

    def list_messages(self, *, history_uri: str, chat_id: str) -> List[Dict[str, Any]]:
        # Mock: return 3 messages
        base = str(uuid4())[:8]
        now = int(time())
        return [
            {
                ChatKeys.MESSAGE_ID: f"{base}-{i}",
                ChatKeys.CHAT_ID: chat_id,
                ChatKeys.ROLE: ChatRoles.USER if i % 2 == 0 else ChatRoles.ASSISTANT,
                ChatKeys.CONTENT: f"sample message {i}",
                ChatKeys.TIMESTAMP: now - (60 * (3 - i)),
            }
            for i in range(3)
        ]

    def get_message(self, *, history_uri: str, chat_id: str, message_id: str) -> Dict[str, Any]:
        return {
            ChatKeys.MESSAGE_ID: message_id,
            ChatKeys.CHAT_ID: chat_id,
            ChatKeys.ROLE: ChatRoles.ASSISTANT,
            ChatKeys.CONTENT: f"content for {message_id}",
            ChatKeys.TIMESTAMP: int(time()),
        }

    def create_message(self, *, history_uri: str, chat_id: str, content: str, role: str = ChatRoles.USER) -> Dict[str, Any]:
        new_id = str(uuid4())
        return {
            Keys.MESSAGE: Messages.MESSAGE_CREATED,
            ChatKeys.MESSAGE_ID: new_id,
            ChatKeys.CHAT_ID: chat_id,
            ChatKeys.ROLE: role,
            ChatKeys.CONTENT: content,
            ChatKeys.TIMESTAMP: int(time()),
        }

    def delete_message(self, *, history_uri: str, chat_id: str, message_id: str) -> None:
        return


