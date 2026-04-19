
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
import enum
from app.models.job import Job

class PackageTier(str, enum.Enum):
    free = "free"
    premium = "premium"
    enterprise = "enterprise"


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id")
    package: PackageTier
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime  
    amount_paid: float 
    is_active: bool = Field(default=True)
    company: "Company" = Relationship(back_populates="subscriptions")