from enum import Enum
from pydantic import BaseModel, EmailStr, UUID4
from typing import Dict, List, Literal, Optional
from datetime import datetime

from src.constant.task_constants import ContributorTaskStatus


class TaskModel(BaseModel):
    id: str
    project_id: str
    prompt_id: str
    type: str
    domain: str
    category: str
    status: str
    deadline: datetime
    submissions_count: int
    reviews_count: int
    accepted_count: int
    rejected_count: int
    created_at: datetime
    updated_at: datetime


class TaskListResponseModel(BaseModel):
    data: List[TaskModel]


class TaskAllocation(BaseModel):
    task_id: str
    assignment_id: str
    prompt_id: str
    sentence_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    assigned_at: datetime
    status: str


class PromptInfoModel(BaseModel):
    prompt_id: str
    sentence_id: str
    sentence_text: str
    media_url: Optional[str] = None
    category: str
    domain: str
    max_reuses: int
    current_reuses: int


class SubmissionInfoModel(BaseModel):
    submission_id: str
    user_id: str
    user_email: str
    type: str
    payload_text: str
    file_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


class ReviewModel(BaseModel):
    reviewer_id: UUID4
    reviewer_email: EmailStr
    # review_scores: Dict[str, int]
    review_total_score: int
    review_decision: Literal["accept", "redo", "rejected"]
    reviewer_comments: Optional[List[str]] = None
    predefined_comments: Optional[List[str]] = None
    total_coins_earned: int


class ReviewInfoModel(BaseModel):
    reviewers: List[ReviewModel]


class AllocationType(str, Enum):
    AGENT_ALLOCATION = "agent_allocation"
    REVIEWER_ALLOCATION = "reviewer_allocation"


class TaskDetailResponseModel(BaseModel):
    type: AllocationType
    allocation_id: str
    task_id: str
    status: ContributorTaskStatus
    assigned_at: datetime
    agent_email: str
    agent_name: str
    submission_id: Optional[str] = None
    sentence: Optional[str] = None
    sentence_id: Optional[str] = None
    file_url: Optional[str] = None
    review_info: Optional[dict] = None
