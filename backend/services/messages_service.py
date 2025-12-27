from typing import Any, Dict, List
from backend.core.constants import Messages, Keys, Fields


class MessagesService:
    def list_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        return []

    def get_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        return {Keys.CHAT_ID: chat_id, Keys.MESSAGE_ID: message_id}

    def create_message(self, chat_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {Keys.MESSAGE: Messages.MESSAGE_CREATED, Keys.CHAT_ID: chat_id, Keys.DATA: data}

    def update_message(self, chat_id: str, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            Keys.MESSAGE: Messages.MESSAGE_UPDATED,
            Keys.CHAT_ID: chat_id,
            Keys.MESSAGE_ID: message_id,
            Keys.DATA: data,
        }

    def delete_message(self, chat_id: str, message_id: str) -> None:
        return


