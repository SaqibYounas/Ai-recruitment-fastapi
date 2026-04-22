"""
Job Application Model
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.job import Job


class JobApplicationBase(SQLModel):
    """Base application model"""
    job_id: int = Field(foreign_key="jobs.id", index=True)
    applicant_email: str = Field(index=True, min_length=5, max_length=255)
    applicant_phone: str = Field(max_length=20)
    resume_url: str = Field(max_length=500)
    cv_name: str = Field(max_length=255)


class JobApplication(JobApplicationBase, table=True):
    """Job application database model"""
    __tablename__ = "job_applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    cv_text: Optional[str] = Field(None, description="Extracted text from CV")
    ai_score: Optional[int] = Field(default=0, ge=0, le=100, description="AI matching score")
    ai_summary: Optional[str] = Field(None, description="AI generated summary")
    status: str = Field(default="pending", index=True)
    applied_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = None
    
    job: Optional["Job"] = Relationship()
    
    class Config:
        """Pydantic config"""
        from_attributes = True


class JobApplicationResponse(JobApplicationBase):
    """Job application response schema"""
    id: int
    cv_text: Optional[str] = None
    ai_score: int = 0
    ai_summary: Optional[str] = None
    status: str
    applied_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
