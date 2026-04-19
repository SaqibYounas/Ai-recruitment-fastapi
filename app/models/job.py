from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import uuid
if TYPE_CHECKING:
    from app.models.user import Company 

class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    REMOTE = "remote"
    CONTRACT = "contract"

class JobBase(SQLModel):
    title: str = Field(index=True)
    description: str
    company_name: str
    location: str
    salary_range: Optional[str] = None
    job_type: JobType = JobType.FULL_TIME
    expires_at: Optional[datetime] = Field(
        default=None, 
        description="Date and time when the job posting will expire"
    )

class Job(JobBase, table=True):
    __tablename__ = "jobs" 

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    shareable_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        unique=True,
        index=True
    )
    user_id: str = Field(foreign_key="users.id") 
    company_id: str = Field(foreign_key="companies.id") 
    company: "Company" = Relationship(back_populates="jobs")
    @property
    def shareable_link(self) -> str:
        return f"https://your-portal.com/apply/{self.shareable_id}"

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    user_id: str 
    created_at: datetime
    is_active: bool
    shareable_id: str 
    shareable_link: Optional[str] = None 
    