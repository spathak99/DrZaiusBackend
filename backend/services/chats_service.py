from typing import Any, Dict, List
from backend.core.constants import Messages, Keys, Fields


class ChatsService:
    def list_chats(self) -> List[Dict[str, Any]]:
        return []

    def get_chat(self, chat_id: str) -> Dict[str, Any]:
        return {Fields.ID: chat_id}

    def create_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {Keys.MESSAGE: Messages.CHAT_CREATED, Keys.DATA: data}

    def update_chat(self, chat_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {Keys.MESSAGE: Messages.CHAT_UPDATED, Fields.ID: chat_id, Keys.DATA: data}

    def delete_chat(self, chat_id: str) -> None:
        return


