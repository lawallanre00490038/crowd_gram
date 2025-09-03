from pydantic import BaseModel, ConfigDict, Field

class CompanyInfo(BaseModel):
    id: str = Field(..., alias="_id")
    first_name: str
    last_name: str
    name: str

    model_config = ConfigDict(populate_by_name=True)