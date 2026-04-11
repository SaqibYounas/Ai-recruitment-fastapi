from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime



class CompanySize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"



class CompanyInfo(BaseModel):
    companyName: str
    position: str
    companySize: CompanySize
    industryType: str
    location: str
    user_id:str



class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[CompanyInfo] = None



class UserLogin(BaseModel):
    email: EmailStr
    password: str



class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    company_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}



class RegisterResponse(BaseModel):
    message: str
    user: UserOut



class CompanyResponse(BaseModel):
    message: str
    user: UserOut



class LoginResponse(BaseModel):
    message: str
    user: UserOut
