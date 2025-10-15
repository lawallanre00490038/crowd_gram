from pydantic import BaseModel, RootModel
from typing import List, Optional
from datetime import datetime
from src.models.api2_models.task import TaskDetailResponseModel
from src.models.api2_models.reviewer import ReviewerTaskResponseModel


class Project(BaseModel):
    id: str
    name: str
    description: str
    agent_quota: int
    reviewer_quota: int 
    reuse_count: int 
    agent_coin: float 
    reviewer_coin: float 
    super_reviewer_coin: float 
    agent_amount: float 
    reviewer_amount: float 
    super_reviewer_amount: float 
    is_public: bool
    review_parameters: List[str]
    agent_instructions: str
    reviewer_instructions: str
    super_reviewer_instructions: Optional[str] = None
    review_scale: int 
    review_threshold_percent: int
    total_prompts: int
    total_tasks: int
    total_submissions: int
    num_redo: Optional[int]
    created_at: datetime
    updated_at: datetime
    

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