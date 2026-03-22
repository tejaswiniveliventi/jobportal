from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.application import ApplicationStatus


class JobOut(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str]
    is_remote: bool
    salary_min: Optional[float]
    salary_max: Optional[float]
    source_url: str
    source_board: str
    posted_at: Optional[datetime]
    model_config = {"from_attributes": True}


class ApplicationOut(BaseModel):
    id: str
    user_id: str
    status: ApplicationStatus
    match_score: Optional[float]
    match_reasoning: Optional[str]
    strengths: Optional[list]
    gaps: Optional[list]
    hiring_manager_name: Optional[str]
    hiring_manager_email: Optional[str]
    applied_at: Optional[datetime]
    last_status_change: datetime
    created_at: datetime
    job: JobOut
    model_config = {"from_attributes": True}


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class DashboardStats(BaseModel):
    total_applications: int
    submitted: int
    interviews: int
    offers: int
    rejected: int
    response_rate: float
    top_companies: List[dict]
    weekly_activity: List[dict]


class UserPreferencesUpdate(BaseModel):
    locations: Optional[List[str]] = None
    min_salary: Optional[int] = None
    roles: Optional[List[str]] = None
    exclude_companies: Optional[List[str]] = None
    is_remote_only: Optional[bool] = None


class AutomationSettingsUpdate(BaseModel):
    auto_apply: Optional[bool] = None
    daily_limit: Optional[int] = None
    require_approval: Optional[bool] = None
