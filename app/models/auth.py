from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional
from config.database import engine


class CompanySize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"



class Company(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    companyName: str
    position: str
    companySize: CompanySize
    industryType: str
    location: str



class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str
    email: str = Field(index=True, unique=True)
    password: str

    company_id: Optional[UUID] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)