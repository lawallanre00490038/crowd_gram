from pydantic import BaseModel, RootModel
from typing import List, Optional
from datetime import datetime
from src.models.api2_models.task import TaskDetailResponseModel
from src.models.api2_models.reviewer import ReviewerTaskResponseModel
from src.models.api2_models.task import TaskDetailResponseModel
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, RootModel, field_validator
from typing import List, Optional, Any
from pydantic import BaseModel, RootModel


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    num_redo: int = 0
    return_type: Optional[str] = None
    agent_quota: int = 0
    reviewer_quota: int = 0
    reuse_count: int = 0
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
    predefined_comments: Optional[List[str]] = Field(default_factory=list)
    review_decisions: Optional[List[str]] = Field(default_factory=list)
    review_scale: int = 5
    review_threshold_percent: int = 0
    total_prompts: int = 0
    total_tasks: int = 0
    total_submissions: int = 0
    created_at: datetime
    updated_at: datetime

    # 🧠 Fix: convert None -> []
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


class ProjectTaskRequestModel(BaseModel):
    project_id: str
    email: str
    status: Optional[str] = None
    prompt_id: Optional[str] = None


class ProjectTaskDetailsResponseModel(BaseModel):
    project_id: str
    project_name: str
    tasks: Optional[List[TaskDetailResponseModel]] = None
    reviewers: Optional[List[ReviewerTaskResponseModel]] = None
