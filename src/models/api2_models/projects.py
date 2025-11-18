from enum import Enum
from typing import List, Optional
from datetime import datetime
from src.constant.task_constants import ContributorTaskStatus, ReviewerTaskStatus
from src.models.api2_models.reviewer import ReviewerAllocation
from src.models.api2_models.task import TaskDetailResponseModel
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, RootModel, field_validator

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    num_redo: int = 0
    return_type: Optional[str] = None
    agent_quota: int = 0
    reviewer_quota: int = 0
    agent_instructions: Optional[str] = None
    reviewer_instructions: Optional[str] = None
    super_reviewer_instructions: Optional[str] = None
    is_auto_review: bool = False
    agent_coin: int = 0
    reviewer_coin: int = 0
    super_reviewer_coin: int = 0
    agent_amount: float = 0.0
    reviewer_amount: float = 0.0
    super_reviewer_amount: float = 0.0
    is_public: bool = False

    predefined_comments: List[str] = Field(default_factory=list)
    review_decisions: List[str] = Field(default_factory=list)

    review_scale: int = 5
    review_threshold_percent: int = 0

    total_prompts: int = 0
    total_tasks: int = 0
    total_submissions: int = 0

    created_at: datetime
    updated_at: datetime

    # Fixes cases where API sends null values instead of arrays
    @field_validator("predefined_comments", "review_decisions", mode="before")
    def default_to_list(cls, v):
        return v or []


class ProjectListResponseModel(RootModel[List[Project]]):
    pass


class ProjectUpdateModel(BaseModel):
    name: str
    description: str
    is_public: bool
    agent_coin: float
    reviewer_coin: float


class ContributorRole(str, Enum):
    AGENT = "agent"
    REVIEWER = "reviewer"


class ProjectTaskRequestModel(BaseModel):
    project_id: str
    agent_email: Optional[str] = None
    # optional list of strings
    status: Optional[List[ContributorTaskStatus]]
    start_date: Optional[datetime] = None               # ISO datetime
    end_date: Optional[datetime] = None                 # ISO datetime
    skip: int = 0                                       # default 0
    limit: int = 2                                      # default 2


class ReviewerTaskRequestModel(BaseModel):
    project_id: str
    reviewer_email: Optional[str]
    # optional list of strings
    status: Optional[List[ReviewerTaskStatus]]
    start_date: Optional[datetime] = None               # ISO datetime
    end_date: Optional[datetime] = None                 # ISO datetime
    skip: int = 0                                       # default 0
    limit: int = 2                                      # default 2


class ProjectTaskDetailsResponseModel(BaseModel):
    message: str
    total_count: int
    allocations: List[TaskDetailResponseModel] = []


class ProjectReviewerDetailsResponseModel(BaseModel):
    message: str
    total_count: int
    allocations: List[ReviewerAllocation] = []
