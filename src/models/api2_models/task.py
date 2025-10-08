from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TaskModel(BaseModel):
    id: str
    project_id: str
    prompt_id: str
    type: str = Field(..., description="Type of the task, e.g., Text, Audio, Video, Image")
    domain: str
    category: str
    status: str = Field(..., description="Status of the task, e.g., pending, completed")
    deadline: datetime
    submissions_count: int = Field(..., ge=0)
    reviews_count: int = Field(..., ge=0)
    accepted_count: int = Field(..., ge=0)
    rejected_count: int = Field(..., ge=0)
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
    status: str = Field(..., description="Status of the allocation, e.g., assigned, completed")
    

class PromptInfoModel(BaseModel):
    prompt_id: str
    sentence_id: str
    sentence_text: str
    media_url: Optional[str] = None
    category: str
    domain: str
    max_reuses: int = Field(..., ge=0)
    current_reuses: int = Field(..., ge=0)
    
class SubmissionInfoModel(BaseModel):
    submission_id: str
    user_id: str
    user_email: str
    type: str
    payload_text: str
    file_url: str
    status: str
    created_at: datetime
    updated_at: datetime

class ReviewInfoModel(BaseModel):
    reviewers: List[str]
    

class TaskDetailResponseModel(BaseModel):
    task_id: str
    assignment_id: str
    assigned_at: datetime
    status: str
    prompt: PromptInfoModel
    submissions: Optional[List[SubmissionInfoModel]] = []
    reviews: Optional[List[ReviewInfoModel]] = []
    user_email: str