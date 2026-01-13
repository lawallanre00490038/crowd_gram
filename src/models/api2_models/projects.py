from enum import Enum
from optparse import Option
from typing import List, Optional
from datetime import datetime
from xmlrpc.client import Boolean
from src.constant.task_constants import ContributorTaskStatus, ReviewerTaskStatus, TaskType
from src.models.api2_models.reviewer import ReviewerAllocation
from src.models.api2_models.task import TaskDetailResponseModel
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, RootModel, field_validator

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from pydantic import BaseModel, Field
from typing import Optional

class ProjectModel(BaseModel):
    id: str
    name: Optional[str] = None
    require_geo: bool = False
    reviewer_instructions: str = Field(
        default="No specific instructions provided."
    )
    agent_instructions: str = Field(
        default="Please translate carefully."
    )
    return_type: TaskType = Field(default=TaskType.TEXT)
    is_check_fmcg: Optional[Boolean] = None
    is_reciept_keywords: Optional[Boolean] = None
    image_category: Optional[str] = None 

class UserProjectState(BaseModel):
    user_email: str
    project_index: int
    projects_details: List[ProjectModel]


class ExtractedProjectInfo(BaseModel):
    email: str
    id: str
    name: Optional[str]
    reviewer_instructions: str
    instruction: str
    return_type: TaskType
    require_geo: bool = False
    max_submit: Optional[int] = None
    cur_submit: Optional[int] = None
    is_check_fmcg: Optional[Boolean] = None
    is_reciept_keywords: Optional[Boolean] = None
    image_category: Optional[str] = None


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

    require_geo: bool = False
    total_prompts: int = 0
    total_tasks: int = 0
    total_submissions: int = 0

    created_at: datetime
    updated_at: datetime

    is_check_fmcg: Optional[Boolean] = False
    is_reciept_keywords: Optional[Boolean] = False
    image_category: Optional[str] = None

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
    status: Optional[List[ContributorTaskStatus]] = []
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

class Prompt(BaseModel):
    prompt_id: str
    sentence_id: str
    sentence_text: str
    media_url: Optional[str] = None
    category: str
    domain: str

class Submission(BaseModel):
    submission_id: str
    project_id: str
    task_id: str
    agent_allocation_id: str
    user_id: str
    user_email: str
    type: str
    payload_text: str
    file_url: str
    status: str
    num_redo: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    prompt: Prompt


from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class ReviewAssignment(BaseModel):
    reviewer_id: str
    id: str
    assigned_at: datetime
    reviewed_at: Optional[datetime] = None
    updated_at: datetime
    submission_id: str
    status: str
    decision: Optional[str] = None
    created_at: datetime


# If your endpoint returns the whole list:
ReviewAssignmentsResponse = List[ReviewAssignment]
