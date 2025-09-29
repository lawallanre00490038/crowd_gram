from pydantic import BaseModel
from typing import List, Optional

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
    

class TelegramStatusModel(BaseModel):
    """Model for Telegram status."""
    email: str