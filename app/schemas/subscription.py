"""
Subscription Schemas
"""
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class PackageTier(str, Enum):
    """Package tier enumeration"""
    free = "free"
    premium = "premium"
    enterprise = "enterprise"


class SubscriptionCreate(BaseModel):
    """Subscription creation schema"""
    package: PackageTier = Field(..., description="Package tier")
    amount_paid: float = Field(..., gt=0, description="Amount paid")
    transaction_id: str = Field(..., min_length=1, description="Transaction ID")

    class Config:
        schema_extra = {
            "example": {
                "package": "premium",
                "amount_paid": 99.99,
                "transaction_id": "txn_123456"
            }
        }


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    id: str = Field(..., description="Subscription ID")
    company_id: str = Field(..., description="Company ID")
    package: PackageTier = Field(..., description="Package tier")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    amount_paid: float = Field(..., description="Amount paid")
    is_active: bool = Field(..., description="Active status")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "sub_123",
                "company_id": "comp_123",
                "package": "premium",
                "start_date": "2024-01-15T10:30:00",
                "end_date": "2024-02-15T10:30:00",
                "amount_paid": 99.99,
                "is_active": True
            }
        }
