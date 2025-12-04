from typing import Any, Dict
from backend.core.constants import Messages


class SecurityService:
    def create_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.POLICY_CREATED, "data": data}

    def update_policy(self, policy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.POLICY_UPDATED, "id": policy_id, "data": data}

    def delete_policy(self, policy_id: str) -> None:
        return

    def generate_key_pair(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.KEY_PAIR_GENERATED}


