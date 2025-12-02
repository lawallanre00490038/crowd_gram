from uuid import UUID
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, RootModel,  HttpUrl, EmailStr
from src.constant.task_constants import ReviewerTaskStatus
from src.models.api2_models.task import TaskDetailResponseModel


class ReviewerModel(BaseModel):
    project_id: str
    submission_id: str
    reviewer_id: str


class UploadReviewModel(BaseModel):
    project_id: str
    file: Optional[str]


class ReviewScores(RootModel[Dict[str, int]]):
    pass


class ReviewModel(BaseModel):
    submission_id: str
    project_id: str
    reviewer_identifier: str
    decision: str
    reviewer_comments: Optional[List[str]] = None


class ReviewFilterModel(BaseModel):
    reviewer_identifier: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None


class ReviewFilterResponseModel(BaseModel):
    reviewer_identifier: str
    submission_id: str
    sentence_id: str
    prompt: str
    file_url: Optional[str] = None
    payload_text: Optional[str] = None
    contributor_id: str
    status: str
    assigned_at: Optional[datetime] = None


class UpdateReviewModel(BaseModel):
    review_id: str
    comments: Optional[str] = None
    scores: Optional[ReviewScores] = None


class ReviewerTaskResponseModel(BaseModel):
    reviewer_id: str
    reviewer_email: str
    tasks: List[TaskDetailResponseModel]


class ReviewerHistoryRequestModel(BaseModel):
    reviewer_identifier: str
    project_id: Optional[str] = None


class ReviewerHistoryResponseModel(BaseModel):
    submission_id: str
    sentence_id: str
    prompt: str
    contributor_id: str
    status: str
    reviewed_at: Optional[datetime] = None


class ReviewerHistoryResponseListModel(RootModel[List[ReviewerHistoryResponseModel]]):
    pass


class ReviewSubmissionResponse(BaseModel):
    submission_status: str
    score: float
    approved: bool
    predefined_comments: Optional[List[str]] = None
    reviewer_comments: Optional[List[str]] = None
    scored_percent: float


class ReviewerAllocation(BaseModel):
    reviewer_allocation_id: UUID
    submission_id: UUID
    reviewer_id: str
    agent_id: str

    sentence_id: str
    sentence: str
    payload_text: Optional[str] = None
    file_url: Optional[HttpUrl] = None

    reviewer_email: Optional[EmailStr] = None
    reviewer_name: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    agent_email: Optional[EmailStr] = None
    agent_name: Optional[str] = None
    status: ReviewerTaskStatus
    assigned_at: datetime
    agent_submission_date: datetime
