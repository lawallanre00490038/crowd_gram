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
    total: int
    number_assigned: int
    total_submissions: int
    approved: int
    rejected: int
    pending: int
    total_coins_earned: int
    total_amount_earned: float

class ProjectReviewStats(BaseModel):
    project_id: str
    project_name: str
    total_reviewed: int
    approved: int
    rejected: int
    pending: int
    number_assigned: int
    total_coins_earned: int
    total_amount_earned: float

class StatusContributorResponseModel(BaseModel):
    user_email: str
    approved: int
    pending: int
    rejected: int
    per_project: List[ProjectStats] = []
    

class StatusReviewerResponseModel(BaseModel):
    reviewer_email: str
    total_reviews: int
    approved_reviews: int
    rejected_reviews: int
    pending_reviews: int
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
    audio_submissions: int
    text_submissions: int
    image_submissions: int
    video_submissions: int
    total_submissions: int


class DailyAnalyticsResponseModel(BaseModel):
    data: List[DailyAnalytics]