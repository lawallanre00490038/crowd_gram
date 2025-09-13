from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Union
from datetime import datetime

from src.models.auth_models import BaseUserData

class CountryModel(BaseModel):
    country: str = Field(..., alias="name")
    country_id: str = Field(..., alias="isoCode")

    model_config = ConfigDict(populate_by_name=True)

class StateModel(BaseModel):
    state: str = Field(..., alias="name")
    state_id: str = Field(..., alias="isoCode")

    model_config = ConfigDict(populate_by_name=True)

class CompanyInfo(BaseModel):
    id: str = Field(..., alias="_id")
    first_name: str
    last_name: str
    name: str

    model_config = ConfigDict(populate_by_name=True)

class FieldData(BaseModel):
    name: str
    field_id: str


class ResultItem(BaseModel):
    id: str = Field(..., alias="_id")
    field_data: List[FieldData]

    model_config = ConfigDict(populate_by_name=True)

class Data(BaseModel):
    result: List[ResultItem]
    totalCount: int


class SignUpResponseModel(BaseModel):
    message: str
    data: Data

class BaseLanguage(BaseModel):
    id: str = Field(..., alias="_id")
    name: str

    model_config = ConfigDict(populate_by_name=True)

class Language(BaseLanguage):
    dialects: List[str]
    status: int
    createdAt: datetime
    updatedAt: datetime
    company_id: str

class LanguageResponseModel(BaseModel):
    message: str
    data: List[Language]

class CategoryQuestion(BaseModel):
    id: str = Field(..., alias="_id")
    category_id: str
    question: str = "No question text"
    company_id: str
    selection: str
    options: List[str] = []
    status: int
    createdAt: datetime
    updatedAt: datetime

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }


class Category(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    status: int
    createdAt: datetime
    updatedAt: datetime
    url: str
    categoryQuestions: List[CategoryQuestion] = []

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }

class Languages(BaseModel):
    lang_id: str
    dialects: str
    proficiency: Dict = {
        "speaking": "Basic",
        "writing": "Basic"
      },
    task_types: List = [] 

class TaskAnswerItem(BaseModel):
    category_id: str
    category_name: str
    ques_id: str
    question: str
    answer: List[str]

class CompleteProfileRequest(BaseModel):
    referal_code: str
    task_answer: List[TaskAnswerItem]
    data_kind: List[str]
    languages: List[Languages]
    city: str
    industry: str
    education_level: str
    age_range: str
    gender: str
    city_id: str
    state_origin_id: str
    country_id: str
    state_origin: str
    country: str
    user_id: str

# Adjust this type alias to match your actual expected response format
CompleteProfileResponseDict = Dict[str, Union[bool, str, BaseUserData | dict]]
