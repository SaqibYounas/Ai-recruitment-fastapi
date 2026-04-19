from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    REMOTE = "remote"
    CONTRACT = "contract"



class JobBase(BaseModel):
    title: str
    description: str
    company_name: str
    location: str
    salary_range: Optional[str] = None
    job_type: JobType = JobType.FULL_TIME
    requirements: Optional[str] = None



class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[JobType] = None
    is_active: Optional[bool] = None



class JobResponse(JobBase):
    id: int
    user_id: int
    created_at: datetime
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)
