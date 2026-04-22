"""
User and Company Models
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4
from datetime import datetime
import enum

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.subscription import Subscription


class CompanySize(str, enum.Enum):
    """Company size enumeration"""
    small = "small"
    medium = "medium"
    large = "large"


class Company(SQLModel, table=True):
    """Company database model"""
    __tablename__ = "companies"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Company ID"
    )
    company_name: str = Field(
        index=True,
        min_length=1,
        max_length=255,
        description="Company name"
    )
    position: str = Field(
        min_length=1,
        max_length=255,
        description="Position in company"
    )
    company_size: CompanySize = Field(description="Company size")
    industry_type: str = Field(
        min_length=1,
        max_length=255,
        description="Industry type"
    )
    location: str = Field(
        min_length=1,
        max_length=255,
        description="Company location"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    package: str = Field(default="free", description="Current active package tier")
    subscriptions: List["Subscription"] = Relationship(back_populates="company")
    users: List["User"] = Relationship(back_populates="company")
    jobs: List["Job"] = Relationship(back_populates="company")


class User(SQLModel, table=True):
    """User database model"""
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="User ID"
    )
    name: str = Field(
        min_length=1,
        max_length=255,
        description="User full name"
    )
    email: str = Field(
        unique=True,
        index=True,
        min_length=5,
        max_length=255,
        description="User email address"
    )
    password: str = Field(
        min_length=8,
        description="Hashed password"
    )
    company_id: Optional[str] = Field(
        default=None,
        foreign_key="companies.id",
        description="Associated company ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    company: Optional[Company] = Relationship(back_populates="users")


def create_db(engine) -> None:
    """
    Create database tables
    
    Args:
        engine: SQLModel engine instance
    """
    SQLModel.metadata.create_all(engine)
