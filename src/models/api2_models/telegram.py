from pydantic import BaseModel
from typing import List, Optional, TypedDict

class RegisterModel(BaseModel):
    """Model for user registration."""
    name: str
    email: str
    password: str
    telegram_id: str
    languages: List[str]
    dialects: List[str]
    

class LoginModel(BaseModel):
    """Model for user login."""
    email: str
    password: Optional[str]
    

class LoginResponseModel(BaseModel):
    """Model for login response."""
    message: Optional[str] = None
    id: str
    email: str
    name: Optional[str] = None
    telegram_id: Optional[str] = None
    role: str
    languages: Optional[List[str]] = []
    dialects: Optional[List[str]] = []
    

class TelegramStatusModel(BaseModel):
    """Model for Telegram status."""
    email: str


class RegisterResponseDict(TypedDict):
    success: bool
    error: str
    base_info: Optional[RegisterModel]

class LoginResponseDict(TypedDict):
    success: bool
    error: str
    base_info: Optional[LoginResponseModel]