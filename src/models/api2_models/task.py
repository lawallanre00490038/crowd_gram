from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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
    submission: Optional[SubmissionInfoModel] = None
    review: Optional[ReviewInfoModel] = None
    user_email: Optional[str] = None