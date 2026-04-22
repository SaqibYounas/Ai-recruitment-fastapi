"""
Job Schemas and Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    """Job type enumeration"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    REMOTE = "remote"
    CONTRACT = "contract"


class JobBase(BaseModel):
    """Base job schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    description: str = Field(..., min_length=10, max_length=5000, description="Job description")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    location: str = Field(..., min_length=1, max_length=255, description="Job location")
    salary_range: Optional[str] = Field(None, max_length=100, description="Salary range")
    job_type: JobType = Field(default=JobType.FULL_TIME, description="Job type")

    class Config:
        schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "description": "Looking for an experienced Python developer...",
                "company_name": "Tech Corp",
                "location": "New York, NY",
                "salary_range": "$120K - $180K",
                "job_type": "full-time"
            }
        }


class JobCreate(JobBase):
    """Job creation schema"""
    pass


class JobUpdate(BaseModel):
    """Job update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    job_type: Optional[JobType] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    """Job response schema"""
    id: int = Field(..., description="Job ID")
    user_id: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Active status")
    shareable_id: str = Field(..., description="Shareable ID for public access")
    shareable_link: Optional[str] = Field(None, description="Public application link")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Senior Python Developer",
                "description": "Looking for an experienced Python developer...",
                "company_name": "Tech Corp",
                "location": "New York, NY",
                "salary_range": "$120K - $180K",
                "job_type": "full-time",
                "user_id": "user-123",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": None,
                "is_active": True,
                "shareable_id": "abc12345",
                "shareable_link": "https://portal.example.com/apply/abc12345"
            }
        }

