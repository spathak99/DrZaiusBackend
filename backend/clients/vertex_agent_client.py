from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4
from time import time

from backend.core.settings import get_settings
from backend.core.constants import ChatKeys, ChatRoles


class VertexAgentClient:
    """
    Thin client stub for Vertex AI Agent Engine APIs (chat agent).
    Replace stubbed bodies with real calls when wiring to Vertex.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.project_id = self.settings.gcp_project_id
        self.location = self.settings.gcp_location
        self.endpoint = self.settings.vertex_agent_api_endpoint.format(location=self.location)
        self.default_agent_id = self.settings.vertex_default_agent_id

    def start_or_get_thread(self, *, user_id: str) -> str:
        # STUB: Return a synthetic thread id
        return f"thr-{user_id}-{str(uuid4())[:8]}"

    def send_message(self, *, thread_id: str, role: str, content: str) -> Dict[str, Any]:
        # STUB: Echo back a mock assistant response
        return {
            ChatKeys.MESSAGE_ID: str(uuid4()),
            ChatKeys.CHAT_ID: thread_id,
            ChatKeys.ROLE: ChatRoles.ASSISTANT,
            ChatKeys.CONTENT: f"echo: {content}",
            ChatKeys.TIMESTAMP: int(time()),
        }

    def list_messages(self, *, thread_id: str) -> List[Dict[str, Any]]:
        # STUB: return empty list
        return []

    def delete_message(self, *, thread_id: str, message_id: str) -> None:
        # STUB: No-op
        return


