from pydantic import BaseModel, EmailStr
from enum import Enum



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



class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: CompanyInfo



class UserLogin(BaseModel):
    email:EmailStr
    password:str
