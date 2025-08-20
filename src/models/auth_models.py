from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class Beneficiary(BaseModel):
    _id: str
    beneficiary_id: Any  # Replace with str or int if the actual type is known
    account_bank: str
    account_number: str
    beneficiary_name: str
    bank_name: str
    account_name: str
    currency: str


class UserData(BaseModel):
    _id: str
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
    otp: int
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
    test_submit_date: Optional[datetime]
    token: str
    refresh_token: str


class LoginResponse(BaseModel):
    message: str
    data: UserData
