from pydantic import BaseModel, RootModel
from typing import Dict, List, Optional
from datetime import datetime
from src.models.api2_models.task import TaskDetailResponseModel

class ReviewerModel(BaseModel):
    project_id: str
    submission_id: str
    reviewer_id: str
    

class UploadReviewModel(BaseModel):
    project_id: str
    file: Optional[str] 
    

class ReviewScores(RootModel[Dict[str, int]]):
    pass


class ReviewModel(BaseModel):
    submission_id: str
    project_id: str
    reviewer_identifier: str
    comments: Optional[str] = None
    scores: ReviewScores
    
class ReviewFilterModel(BaseModel):
    reviewer_identifier: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None
    
class ReviewFilterResponseModel(BaseModel):
    reviewer_identifier: str
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
    reviewer_identifier: str
    project_id: Optional[str] = None
    
class ReviewerHistoryResponseModel(BaseModel):
    submission_id: str
    sentence_id: str
    prompt: str
    contributor_id: str
    status: str
    reviewed_at: Optional[datetime] = None

class ReviewerHistoryResponseListModel(RootModel[List[ReviewerHistoryResponseModel]]):
    pass