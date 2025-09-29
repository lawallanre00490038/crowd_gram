from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from src.models.api2_models.task import TaskDetailResponseModel

class ReviewerModel(BaseModel):
    project_id: str
    submission_id: str
    reviewer_id: str
    

class UploadReviewModel(BaseModel):
    project_id: str
    file: Optional[str] = Field(
        None,
        description="File reference (nullable). Can be a string or BSON $binary object"
    )
    

class ReviewScores(BaseModel):
    __root__: Dict[str, int]  # Dynamic keys with integer values
    

class ReviewModel(BaseModel):
    submission_id: str
    project_id: str
    reviewer_id: str
    comments: Optional[str] = None
    scores: ReviewScores
    
class ReviewFilterModel(BaseModel):
    reviewer_id: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None
    
class ReviewFilterResponseModel(BaseModel):
    reviewer_id: str
    submission_id: str
    sentence_id: str
    prompt: str
    file_url: Optional[str] = None
    payload_text: Optional[str] = None
    contributor_id: str
    status: str
    assigned_at: Optional[datetime] = None

class UpdateReviewModel(BaseModel):
    review_id: str
    comments: Optional[str] = None
    scores: Optional[ReviewScores] = None

class ReviewerTaskResponseModel(BaseModel):
    reviewer_id: str
    reviewer_email: str
    tasks: List[TaskDetailResponseModel]
    

class ReviewerHistoryRequestModel(BaseModel):
    reviewer_id: str
    project_id: Optional[str] = None
    
class ReviewerHistoryResponseModel(BaseModel):
    submission_id: str
    sentence_id: str
    prompt: str
    contributor_id: str
    status: str
    reviewed_at: Optional[datetime] = None

class ReviewerHistoryResponseListModel(BaseModel):
    __root__: List[ReviewerHistoryResponseModel]