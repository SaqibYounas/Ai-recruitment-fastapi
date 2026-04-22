"""
Subscription Model
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import enum

# Circular import se bachne ke liye TYPE_CHECKING use karein
if TYPE_CHECKING:
    from app.models.user import Company

class PackageTier(str, enum.Enum):
    """Package tier enumeration"""
    free = "free"
    premium = "premium"
    enterprise = "enterprise"


class Subscription(SQLModel, table=True):
    """Subscription database model"""
    __tablename__ = "subscriptions"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Subscription ID"
    )
    company_id: str = Field(
        foreign_key="companies.id",
        index=True,
        description="Associated company ID"
    )
    package: PackageTier = Field(
        index=True,
        description="Subscription package tier"
    )
    start_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Subscription start date"
    )
    end_date: datetime = Field(description="Subscription end date")
    amount_paid: float = Field(
        ge=0,
        description="Amount paid for subscription"
    )
    is_active: bool = Field(
        default=True,
        index=True,
        description="Active status"
    )
    
    # FIXED LINE: Added missing quote, equals sign, and corrected Relationship spelling
    company: Optional["Company"] = Relationship(back_populates="subscriptions")