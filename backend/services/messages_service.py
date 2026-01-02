"""
Messages service: stubbed operations for CRUD on chat messages.
"""
from typing import Any, Dict, List
from backend.core.constants import Messages, Keys


class MessagesService:
    """Service providing message CRUD operations (stubbed for pre-MVP)."""
    def list_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Return a list of messages for a chat (currently empty stub)."""
        return []

    def get_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        """Return a single message stub payload."""
        return {Keys.CHAT_ID: chat_id, Keys.MESSAGE_ID: message_id}

    def create_message(self, chat_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a message (stub) and return a confirmation payload."""
        return {Keys.MESSAGE: Messages.MESSAGE_CREATED, Keys.CHAT_ID: chat_id, Keys.DATA: data}

    def update_message(self, chat_id: str, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message (stub) and return a confirmation payload."""
        return {
            Keys.MESSAGE: Messages.MESSAGE_UPDATED,
            Keys.CHAT_ID: chat_id,
            Keys.MESSAGE_ID: message_id,
            Keys.DATA: data,
        }

    def delete_message(self, chat_id: str, message_id: str) -> None:
        """Delete a message (stub)."""
        return


