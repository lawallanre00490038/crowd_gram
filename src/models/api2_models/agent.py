from pydantic import BaseModel, RootModel
from typing import List, Optional, Union
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


class SubmissionListResponseModel(RootModel[List[SubmissionResponseModel]]):
    """Model representing a list of submissions."""
    pass


class SubmissionFilterModel(BaseModel):
    """Model for filtering submissions."""
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    status: Optional[str] = None
