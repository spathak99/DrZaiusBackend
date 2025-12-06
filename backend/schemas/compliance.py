from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import Timestamped


class HipaaReportResponse(BaseModel):
    report: str


class RiskAssessmentCreate(BaseModel):
    scope: Optional[str] = None
    metadata: Optional[dict] = None


class RiskAssessmentResponse(Timestamped):
    id: UUID
    scope: Optional[str] = None
    status: str
    result: Optional[dict] = None


class IncidentCreate(BaseModel):
    summary: str
    severity: str
    details: Optional[dict] = None


class IncidentResponse(Timestamped):
    id: UUID
    summary: str
    severity: str
    status: str


