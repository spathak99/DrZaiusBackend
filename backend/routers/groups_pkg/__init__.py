from __future__ import annotations

from fastapi import APIRouter, Depends
from backend.core.constants import Prefix, Tags
from backend.routers.deps import get_current_user

from .core import router as core_router
from .dependents import router as dependents_router
from .invites import router as invites_router

router = APIRouter(prefix=Prefix.GROUPS, tags=[Tags.GROUPS], dependencies=[Depends(get_current_user)])
router.include_router(core_router)
router.include_router(dependents_router)
router.include_router(invites_router)


