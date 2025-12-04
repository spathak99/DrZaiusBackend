from typing import Any, Dict, List
from backend.core.constants import Messages


class ChatsService:
    def list_chats(self) -> List[Dict[str, Any]]:
        return []

    def get_chat(self, chat_id: str) -> Dict[str, Any]:
        return {"id": chat_id}

    def create_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.CHAT_CREATED, "data": data}

    def update_chat(self, chat_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.CHAT_UPDATED, "id": chat_id, "data": data}

    def delete_chat(self, chat_id: str) -> None:
        return


