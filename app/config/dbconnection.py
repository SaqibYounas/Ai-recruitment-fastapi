from sqlmodel import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

engine = create_engine(
settings.DATABASE_URL,
pool_size=10, max_overflow=20 
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
