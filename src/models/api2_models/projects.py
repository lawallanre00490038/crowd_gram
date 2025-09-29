from pydantic import BaseModel, Field
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
    agent_coin: int = Field(..., ge=0)
    reviewer_coin: int = Field(..., ge=0)
    super_reviewer_coin: int = Field(..., ge=0)
    agent_amount: int = Field(..., ge=0)
    reviewer_amount: int = Field(..., ge=0)
    super_reviewer_amount: int = Field(..., ge=0)
    is_public: bool
    review_parameters: List[str]
    review_scale: int = Field(..., ge=1)
    review_threshold_percent: int = Field(..., ge=0, le=100)
    total_prompts: int = Field(..., ge=0)
    total_tasks: int = Field(..., ge=0)
    total_submissions: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime
    
    
class ProjectListResponseModel(BaseModel):
    data: List[Project]
    

class ProjectUpdateModel(BaseModel):
    name: str
    description: str
    is_public: bool
    agent_coin: int = Field(..., ge=0)
    reviewer_coin: int = Field(..., ge=0)
    

class ContributorProjectTaskRequestModel(BaseModel):
    project_id: str
    status: Optional[str] = None  # e.g., "pending", "completed"
    user_email: Optional[str] = None  # Filter by user email if needed
    user_id: Optional[str] = None  # Filter by user ID if needed
    prompt_id: Optional[str] = None  # Filter by prompt ID if needed
    

class ReviewerProjectTaskRequestModel(BaseModel):
    project_id: str
    status: Optional[str] = None  # e.g., "pending", "completed"
    reviewer_email: Optional[str] = None  # Filter by reviewer email if needed
    reviewer_id: Optional[str] = None  # Filter by reviewer ID if needed
    prompt_id: Optional[str] = None  # Filter by prompt ID if needed

class ProjectTaskAllocationResponseModel(BaseModel):
    project_id: str
    project_name: str
    allocations: List[TaskAllocation]
    

class ProjectTaskDetailsResponseModel(BaseModel):
    project_id: str
    project_name: str
    tasks: List[TaskDetailResponseModel]
    

class ReviewerProjectAssignedTasksResponseModel(BaseModel):
    project_id: str
    project_name: str
    reviewers: List[ReviewerTaskResponseModel]
    