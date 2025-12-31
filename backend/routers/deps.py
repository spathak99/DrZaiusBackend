from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.constants import Errors, Auth as AuthConst, Messages
from backend.db.database import get_db
from backend.db.models import User
from backend.services.auth_service import AuthService
from backend.services.groups_service import GroupsService, MembershipsService
from backend.services.payment_codes_service import PaymentCodesService
from backend.services.invitations_service import InvitationsService
from backend.services.access_service import AccessService
from backend.services import DocsService, IngestionService
from backend.services.dlp_service import DlpService
from backend.repositories.groups_repo import GroupsRepository
from backend.repositories.group_memberships_repo import GroupMembershipsRepository
from backend.repositories.payment_codes_repo import PaymentCodesRepository
from backend.repositories.invitations_repo import InvitationsRepository
from backend.repositories.access_repo import AccessRepository
from backend.repositories.group_member_invites_repo import GroupMemberInvitesRepository
from backend.services.group_member_invites_service import GroupMemberInvitesService


auth_service = AuthService()


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
    scheme, _, token = authorization.partition(" ")
    if not token or scheme.lower() != Messages.TOKEN_TYPE_BEARER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
    try:
        payload = auth_service.verify_token(token)
        user_id = payload.get(AuthConst.JWT_CLAIM_SUB)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        # Coerce to UUID for safety
        try:
            user_uuid = UUID(user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        user = db.scalar(select(User).where(User.id == user_uuid))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.INVALID_CREDENTIALS)



# Service factories (constructor-based DI)
def get_groups_service() -> GroupsService:
	return GroupsService(groups_repo=GroupsRepository(), members_repo=GroupMembershipsRepository())


def get_memberships_service() -> MembershipsService:
	return MembershipsService(groups_repo=GroupsRepository(), memberships_repo=GroupMembershipsRepository())


def get_payment_codes_service() -> PaymentCodesService:
	return PaymentCodesService(repo=PaymentCodesRepository(), members=GroupMembershipsRepository(), groups=GroupsRepository())


def get_invitations_service() -> InvitationsService:
	return InvitationsService(repo=InvitationsRepository())


def get_access_service() -> AccessService:
	return AccessService(repo=AccessRepository())


def get_docs_service() -> DocsService:
	return DocsService()


def get_ingestion_service() -> IngestionService:
	return IngestionService()


def get_dlp_service() -> DlpService:
	return DlpService()


def get_group_member_invites_service() -> GroupMemberInvitesService:
	return GroupMemberInvitesService(repo=GroupMemberInvitesRepository(), memberships=GroupMembershipsRepository())

