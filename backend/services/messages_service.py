from typing import Any, Dict, List


class MessagesService:
    def list_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        return []

    def get_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        return {"chatId": chat_id, "messageId": message_id}

    def create_message(self, chat_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "message created", "chatId": chat_id, "data": data}

    def update_message(self, chat_id: str, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "message updated", "chatId": chat_id, "messageId": message_id, "data": data}

    def delete_message(self, chat_id: str, message_id: str) -> None:
        return


