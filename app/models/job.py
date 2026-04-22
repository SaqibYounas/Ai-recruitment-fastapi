"""
Job Model
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import uuid

if TYPE_CHECKING:
    from app.models.user import Company


class JobType(str, Enum):
    """Job type enumeration"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    REMOTE = "remote"
    CONTRACT = "contract"


class JobBase(SQLModel):
    """Base job model"""
    title: str = Field(index=True, min_length=1, max_length=255)
    description: str = Field(min_length=10, max_length=5000)
    company_name: str = Field(index=True, min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    job_type: JobType = Field(default=JobType.FULL_TIME)
    expires_at: Optional[datetime] = Field(
        None,
        description="Date and time when job posting expires"
    )


class Job(JobBase, table=True):
    """Job database model"""
    __tablename__ = "jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True, index=True)
    shareable_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        unique=True,
        index=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    
    company: Optional["Company"] = Relationship(back_populates="jobs")
    
    @property
    def shareable_link(self) -> str:
        """Generate shareable link for job posting"""
        return f"https://your-portal.com/apply/{self.shareable_id}"


class JobCreate(JobBase):
    """Job creation schema"""
    pass


class JobResponse(JobBase):
    """Job response schema"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    shareable_id: str
    shareable_link: Optional[str] = None
    
    class Config:
        from_attributes = True

    