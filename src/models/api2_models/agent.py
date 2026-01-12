from ast import Dict
from optparse import Option
from xmlrpc.client import Boolean
from pydantic import BaseModel, RootModel, Field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from src.models.api2_models.task import PromptInfoModel


class SubmissionModel(BaseModel):
    """Model for creating a new submission."""
    project_id: str
    task_id: str
    agent_allocation_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    type: Optional[str] = None
    payload_text: Optional[str] = None
    telegram_file_id: Optional[str] = None
    file: Optional[Union[str, dict]] = None
    meta: Dict[str, Any] = Field(default_factory=dict) 
    is_check_fmcg: Optional[Boolean] = False
    is_reciept_keywords: Optional[Boolean] = False


class SubmissionResponseModel(BaseModel):
    """Model representing a submission response."""
    submission_id: str
    project_id: str
    task_id: str
    agent_allocation_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    type: Optional[str] = None
    payload_text: Optional[str] = None
    file_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    prompt: Optional[PromptInfoModel] = None
    meta: Optional[Dict] = None 

class ImageMetrics(BaseModel):
    blur_score: float
    rotation:  Optional[float] = None
    skew_angle: Optional[float] = None

class AgentResults(BaseModel):
    quality: str
    orientation: str
    ocr: str
    deduplication: Optional[str] = None
    decision: str

class ImageError(BaseModel):
    code: str
    message: str
    instruction: str
    impact: float
    status: str

class ImageAnalysisResponse(BaseModel):
    success: bool
    decision: str
    confidence: float
    errors: List[ImageError]
    metrics: ImageMetrics
    agent_results: AgentResults



class SubmissionListResponseModel(RootModel[List[SubmissionResponseModel]]):
    """Model representing a list of submissions."""
    pass


class SubmissionFilterModel(BaseModel):
    """Model for filtering submissions."""
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    status: Optional[str] = None
