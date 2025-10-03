from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Union
from datetime import datetime

class PromptModel(BaseModel):
    """Model representing a prompt associated with a submission."""
    prompt_id: str = Field(..., description="Unique ID of the prompt")
    sentence_id: str = Field(..., description="Unique ID of the sentence")
    sentence_text: str = Field(..., description="Text of the sentence")
    media_url: Optional[str] = Field(None, description="URL of the media if applicable")
    category: Optional[str] = Field(None, description="Category of the prompt if applicable")
    domain: Optional[str] = Field(None, description="Domain of the prompt if applicable")


class SubmissionModel(BaseModel):
    """Model for creating a new submission."""
    project_id: str = Field(..., description="Unique ID of the project")  # required
    task_id: str = Field(..., description="Unique ID of the task")  # required
    assignment_id: str = Field(..., description="Unique ID of the assignment")  # required
    user_id: Optional[str] = Field(None, description="User ID (nullable)")
    user_email: Optional[str] = Field(None, description="User email (nullable)")
    type: Optional[str] = Field(None, description="Submission type (nullable, e.g., text, audio, video)")
    payload_text: Optional[str] = Field(None, description="Text payload if provided")
    telegram_file_id: Optional[str] = Field(None, description="Telegram file ID if file is uploaded")
    file: Optional[Union[str, dict]] = Field(
        None,
        description="File reference (nullable). Can be a string or BSON $binary object"
    )
    

class SubmissionResponseModel(BaseModel):
    """Model representing a submission response."""
    submission_id: str = Field(..., description="Unique ID of the submission")
    project_id: str = Field(..., description="Unique ID of the project")
    task_id: str = Field(..., description="Unique ID of the task")
    assignment_id: str = Field(..., description="Unique ID of the assignment")
    user_id: Optional[str] = Field(None, description="User ID (nullable)")
    user_email: Optional[str] = Field(None, description="User email (nullable)")
    type: Optional[str] = Field(None, description="Submission type (nullable, e.g., text, audio, video)")
    payload_text: Optional[str] = Field(None, description="Text payload if provided")
    file_url: Optional[str] = Field(None, description="URL to access the file (nullable)")
    status: str = Field(..., description="Status of the submission (e.g., pending, accepted, rejected)")
    created_at: datetime = Field(..., description="Timestamp when the submission was created")
    updated_at: datetime = Field(..., description="Timestamp when the submission was last updated")
    prompt: PromptModel = Field(..., description="Associated prompt details")


class SubmissionListResponseModel(RootModel[List[SubmissionResponseModel]]):
    """Model representing a list of submissions."""
    pass


class SubmissionFilterModel(BaseModel):
    """Model for filtering submissions."""
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    user_email: Optional[str] = Field(None, description="Filter by user email")
    status: Optional[str] = Field(None, description="Filter by submission status (e.g., pending, accepted, rejected)")