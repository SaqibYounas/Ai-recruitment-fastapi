from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
import enum
from uuid import uuid4
from app.config.dbconnection import Base, engine



class CompanySize(str, enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"



class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    company_name = Column(String, index=True)
    position = Column(String)
    company_size = Column(Enum(CompanySize))
    industry_type = Column(String)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="company")



class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    company_id = Column(String, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    company = relationship("Company", back_populates="users")



def create_db():
    Base.metadata.create_all(bind=engine)
