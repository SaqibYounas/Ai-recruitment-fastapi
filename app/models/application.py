from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    user_id: int = Field(foreign_key="user.id")
    resume_url: str 
    applied_at: datetime = Field(default_factory=datetime.utcnow)


class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    user_id: int = Field(foreign_key="user.id")
    resume_url: str
    # AI Fields
    ai_score: Optional[int] = None
    ai_analysis: Optional[str] = None
    applied_at: datetime = Field(default_factory=datetime.utcnow)