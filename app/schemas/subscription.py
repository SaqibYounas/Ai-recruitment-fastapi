from pydantic import BaseModel
from enum import Enum

class PackageTier(str, Enum):
    free = "free"
    premium = "premium"
    enterprise = "enterprise"

class SubscriptionCreate(BaseModel):
    package: PackageTier
    amount_paid: float  
    transaction_id: str