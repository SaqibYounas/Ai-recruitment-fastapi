# from sqlmodel import SQLModel, Field, Relationship
# from typing import Optional
# from datetime import datetime
# from enum import Enum

# class JobType(str, Enum):
#     FULL_TIME = "full-time"
#     PART_TIME = "part-time"
#     REMOTE = "remote"
#     CONTRACT = "contract"

# class JobBase(SQLModel):
#     title: str = Field(index=True)
#     description: str
#     company_name: str
#     location: str
#     salary_range: Optional[str] = None
#     job_type: JobType = JobType.FULL_TIME

# class Job(JobBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     is_active: bool = Field(default=True)
    
#     user_id: int = Field(foreign_key="user.id") 

# class JobCreate(JobBase):
#     pass

# class JobResponse(JobBase):
#     id: int
#     user_id: int
#     created_at: datetime
#     is_active: bool