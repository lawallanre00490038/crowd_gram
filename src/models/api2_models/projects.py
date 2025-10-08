from pydantic import BaseModel, Field, RootModel
from typing import List, Optional
from datetime import datetime
from src.models.api2_models.task import TaskAllocation, TaskDetailResponseModel
from src.models.api2_models.reviewer import ReviewerTaskResponseModel


class Project(BaseModel):
    id: str
    name: str
    description: str
    per_user_quota: int = Field(..., ge=0)
    reuse_count: int = Field(..., ge=0)
    agent_coin: float = Field(..., ge=0)
    reviewer_coin: float = Field(..., ge=0)
    super_reviewer_coin: float = Field(..., ge=0)
    agent_amount: float = Field(..., ge=0)
    reviewer_amount: float = Field(..., ge=0)
    super_reviewer_amount: float = Field(..., ge=0)
    is_public: bool
    review_parameters: List[str]
    review_scale: int = Field(..., ge=1)
    review_threshold_percent: int = Field(..., ge=0, le=100)
    total_prompts: int = Field(..., ge=0)
    total_tasks: int = Field(..., ge=0)
    total_submissions: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime
    

class ProjectListResponseModel(RootModel[List[Project]]):
    pass
    

class ProjectUpdateModel(BaseModel):
    name: str
    description: str
    is_public: bool
    agent_coin: float = Field(..., ge=0)
    reviewer_coin: float = Field(..., ge=0)


class ProjectTaskRequestModel(BaseModel):
    project_id: str
    email: str
    status: Optional[str] = None
    prompt_id: Optional[str] = None

class ProjectTaskDetailsResponseModel(BaseModel):
    project_id: str
    project_name: str
    tasks: Optional[List[TaskDetailResponseModel]] = None
    reviewer: Optional[List[ReviewerTaskResponseModel]] = None