from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class JobApplication(SQLModel, table=True):
    __tablename__ = "job_applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="jobs.id")
    user_id: str = Field(foreign_key="users.id")
    resume_url: str  
    cv_text: Optional[str] = None 
    ai_score: Optional[int] = Field(default=0)
    ai_summary: Optional[str] = None
    status: str = Field(default="pending") 
    applied_at: datetime = Field(default_factory=datetime.utcnow)