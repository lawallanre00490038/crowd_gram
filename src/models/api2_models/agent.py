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
    image_category: Optional[str] = None


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
    message: Optional[str] = None
    instruction: Optional[str] = None
    impact: Optional[float] = None
    status: Optional[str] = None

class ImageAnalysisResponse(BaseModel):
    success: bool
    decision: Optional[str] = None
    confidence: Optional[float] = None
    errors: Optional[List[ImageError]] = None
    # metrics: Optional[ImageMetrics] = None
    # agent_results: Optional[AgentResults] = None

class SubmissionListResponseModel(RootModel[List[SubmissionResponseModel]]):
    """Model representing a list of submissions."""
    pass


class SubmissionFilterModel(BaseModel):
    """Model for filtering submissions."""
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    status: Optional[str] = None
