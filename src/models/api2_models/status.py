from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StatusModel(BaseModel):
    email: str
    start: datetime
    end: Optional[datetime] = None
    

class ProjectStats(BaseModel):
    project_id: str
    project_name: str
    total: int = Field(..., ge=0)
    number_assigned: int = Field(..., ge=0)
    total_submissions: int = Field(..., ge=0)
    approved: int = Field(..., ge=0)
    rejected: int = Field(..., ge=0)
    pending: int = Field(..., ge=0)
    total_coins_earned: int = Field(..., ge=0)
    total_amount_earned: float = Field(..., ge=0.0)

class ProjectReviewStats(BaseModel):
    project_id: str
    project_name: str
    total_reviewed: int = Field(..., ge=0)
    approved: int = Field(..., ge=0)
    rejected: int = Field(..., ge=0)
    pending: int = Field(..., ge=0)
    number_assigned: int = Field(..., ge=0)
    total_coins_earned: int = Field(..., ge=0)
    total_amount_earned: float = Field(..., ge=0.0)

class StatusContributorResponseModel(BaseModel):
    user_email: str
    approved: int = Field(..., ge=0)
    pending: int = Field(..., ge=0)
    rejected: int = Field(..., ge=0)
    per_project: List[ProjectStats] = []
    

class StatusReviewerResponseModel(BaseModel):
    reviewer_email: str
    total_reviews: int = Field(..., ge=0)
    approved_reviews: int = Field(..., ge=0)
    rejected_reviews: int = Field(..., ge=0)
    pending_reviews: int = Field(..., ge=0)
    per_project: List[ProjectReviewStats] = []
    

class AnalyticsResponseModel(BaseModel):
    total_users: int
    total_projects: int
    total_allocations: int
    total_submissions: int
    approved_submissions: int
    rejected_submissions: int
    pending_review_submissions: int
    total_coins_paid: int


class DailyAnalytics(BaseModel):
    date: datetime
    audio_submissions: int = Field(..., ge=0)
    text_submissions: int = Field(..., ge=0)
    image_submissions: int = Field(..., ge=0)
    video_submissions: int = Field(..., ge=0)
    total_submissions: int = Field(..., ge=0)
    
    
class DailyAnalyticsResponseModel(BaseModel):
    data: List[DailyAnalytics]