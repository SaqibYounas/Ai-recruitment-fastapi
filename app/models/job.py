from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

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
    user_id: str = Field(foreign_key="users.id") 

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    user_id: str 
    created_at: datetime
    is_active: bool
    shareable_link: Optional[str] = None 