"""
Authentication Schemas and Request/Response Models
"""
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class CompanySize(str, Enum):
    """Company size enumeration"""
    small = "small"
    medium = "medium"
    large = "large"


class CompanyInfoCreate(BaseModel):
    """Company information creation schema"""
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    position: str = Field(..., min_length=1, max_length=255, description="Position in company")
    company_size: CompanySize = Field(..., description="Company size")
    industry_type: str = Field(..., min_length=1, max_length=255, description="Industry type")
    location: str = Field(..., min_length=1, max_length=255, description="Company location")

    class Config:
        schema_extra = {
            "example": {
                "company_name": "Tech Corp",
                "position": "HR Manager",
                "company_size": "medium",
                "industry_type": "Technology",
                "location": "New York, NY"
            }
        }


class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    company: Optional[CompanyInfoCreate] = Field(None, description="Optional company info")

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: EmailStr = Field(..., description="User email")
    company_id: Optional[str] = Field(None, description="Associated company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john@example.com",
                "company_id": None,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": None
            }
        }


class CompanyResponse(BaseModel):
    """Company response schema"""
    id: str = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    position: str = Field(..., description="Position in company")
    company_size: CompanySize = Field(..., description="Company size")
    industry_type: str = Field(..., description="Industry type")
    location: str = Field(..., description="Company location")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    """Registration response schema"""
    message: str = Field(..., description="Response message")
    user: UserResponse = Field(..., description="Created user details")

    class Config:
        schema_extra = {
            "example": {
                "message": "Account created successfully",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "company_id": None,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": None
                }
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class CompanyInfoResponse(BaseModel):
    """Company info response schema"""
    message: str = Field(..., description="Response message")
    user: UserResponse = Field(..., description="Updated user details")

    class Config:
        schema_extra = {
            "example": {
                "message": "Company info saved successfully",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "company_id": "456f7890-a12b-34c5-d678-901234567890",
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:35:00"
                }
            }
        }
