from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Any, TypedDict
from datetime import datetime


class Beneficiary(BaseModel):
    id: str = Field(..., alias="_id")
    beneficiary_id: Any  # Replace with str or int if the actual type is known
    account_bank: str
    account_number: str
    beneficiary_name: str
    bank_name: str
    account_name: str
    currency: str

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }

class BaseUserData(BaseModel):
    id: str = Field(..., alias="_id")
    account_source: str
    beneficiaries: List[Beneficiary]
    coins: int
    company_id: str
    country_code: Optional[str]
    createdAt: datetime
    deactivate_message: Optional[str]
    deactivated_by: Optional[str]
    email: str
    fcm_token: List[str]
    is_onboarding: bool
    is_test_submit: bool
    is_tyk_reattempt: bool
    is_verified: bool
    name: str
    os_type: str
    phone_number: Optional[str]
    profile_pic: Optional[str]
    reattempt_count: int
    referal_code: str
    reject_reason: Optional[str]
    social_account: List[Any]
    status: int
    sub_admin_review: bool
    updatedAt: datetime
    user_type: int
    version: str

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }

class UserData(BaseUserData):
    token: str
    refresh_token: str


class LoginResponse(BaseModel):
    message: str
    data: UserData

class UserRegisterRequest(BaseModel):
    country_code: str
    phone_number: str
    email: Optional[EmailStr] = None
    os_type: str
    company_id: str
    password: str
    name: str

class SignupResponseDict(TypedDict):
    success: bool
    error: str
    base_info: BaseUserData

class LoginResponseDict(TypedDict):
    success: bool
    error: str
    base_info: UserData

class VerifyPasswordInput(BaseModel):
    password: str
    otp: str
    email: EmailStr
    phone_number: str