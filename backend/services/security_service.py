from typing import Any, Dict


class SecurityService:
    def create_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "policy created", "data": data}

    def update_policy(self, policy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "policy updated", "id": policy_id, "data": data}

    def delete_policy(self, policy_id: str) -> None:
        return

    def generate_key_pair(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "key pair generated"}


