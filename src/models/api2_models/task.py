from enum import Enum
from pydantic import BaseModel, EmailStr, UUID4
from typing import Dict, List, Literal, Optional
from datetime import datetime

from src.constant.task_constants import ContributorTaskStatus
from uuid import UUID


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

class ReviewDecision(str, Enum):
    ACCEPT = "accept"
    REJECTED = "rejected"


class ReviewEvent(BaseModel):
    type: str
    review_id: UUID
    reviewer_id: UUID
    reviewer_email: EmailStr
    reviewer_name: str
    decision: str
    reviewer_comments: List[str]
    reviewed_at: datetime

class TaskDetailResponseModel(BaseModel):
    # Existing fields, updated if necessary
    agent_allocation_id: str
    task_id: str
    status: ContributorTaskStatus
    assigned_at: datetime
    agent_email: str
    agent_name: Optional[str] = None
    
    # Fields from the new schema
    project_id: str  # Added from new schema
    submission_id: Optional[str] = None
    submitted_at: Optional[datetime] = None  # Added from new schema
    file_url: Optional[str] = None
    payload_text: Optional[str] = None  # Added from new schema
    agent_id: str  # Added from new schema, using agent_id from the new schema
    sentence_id: Optional[str] = None
    sentence: Optional[str] = None
    reviewer_comments: Optional[List[str]] = None  # Replaces review_info's comment field
    review_decision: Optional[ReviewDecision] = None  # Replaces review_info's decision field
    reviewed_at: Optional[datetime] = None  # Replaces review_info's timestamp

    # Removed/Modified fields:
    # reviewer_email: Optional[str] = None  # Removed (not in new schema)
    # reviewer_name: Optional[str] = None    # Removed (not in new schema)
    # review_info: Optional[ReviewEvent] = None  # Replaced by reviewer_comments, review_decision, reviewed_at
