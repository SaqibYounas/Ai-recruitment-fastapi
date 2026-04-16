from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
import enum

# Enums SQLModel ke saath
class CompanySize(str, enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"

# Company Model
class Company(SQLModel, table=True):
    __tablename__ = "companies" # Optional, SQLModel khud handle kar leta hai

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    company_name: str = Field(index=True)
    position: str
    company_size: CompanySize
    industry_type: str
    location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship: Ek company mein many users ho sakte hain
    users: List["User"] = Relationship(back_populates="company")

# User Model
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password: str
    
    # Foreign Key
    company_id: Optional[str] = Field(default=None, foreign_key="companies.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship: User ek hi company se belong karega
    company: Optional[Company] = Relationship(back_populates="users")

# DB Creation function
from app.config.dbconnection import engine

def create_db():
    SQLModel.metadata.create_all(engine)