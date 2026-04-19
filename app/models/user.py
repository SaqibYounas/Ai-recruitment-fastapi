from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4
from datetime import datetime
import enum

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.subscription import Subscription

class CompanySize(str, enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"

class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    company_name: str = Field(index=True)
    position: str
    company_size: CompanySize
    industry_type: str
    location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    subscriptions: List["Subscription"] = Relationship(back_populates="company")
    users: List["User"] = Relationship(back_populates="company")
    jobs: List["Job"] = Relationship(back_populates="company")

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password: str
    company_id: Optional[str] = Field(default=None, foreign_key="companies.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    company: Optional[Company] = Relationship(back_populates="users")
    
def create_db(engine):
    SQLModel.metadata.create_all(engine)