from enum import Enum
from pydantic import BaseModel, Field
from datetime import timedelta
from typing import List, Optional
from datetime import datetime

# Define the Pydantic model for your task data.
# Each field corresponds to a key in your dictionary.
class Task(BaseModel):
    """
    A Pydantic model representing a translation task.
    This model provides data validation and type-hinting for task data.
    """
    category: str
    task_id: str
    deadline: str
    extend_deadline: str
    required_language: str
    required_dialects: str
    task_type: str
    rewards: str
    category_type: str
    task_description: str
    task_instructions: str

class TaskType(Enum):
    Text = "Text"
    Audio = "Audio"
    Video = "Video"
    Image = "Image"


class Category(BaseModel):
    _id: str
    name: str
    status: Optional[int] = None  # Not all items have this field
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    url: Optional[str]
    isAlreadySubmit: bool
    is_exist: bool
    is_category_rejected: bool

class CategoryList(BaseModel):
    result: List[Category]
    totalCount: int

class CategoryListResponseModel(BaseModel):
    message: str
    data: CategoryList

class TaskDetail(BaseModel):
    task_id: str
    required_language: str
    min_duration: timedelta
    max_duration: timedelta

class ResponseModel(BaseModel):
    status: bool
    message: str
    data: str
    code: int
