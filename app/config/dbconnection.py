from sqlmodel import create_engine, Session, SQLModel
from app.core.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10, 
    max_overflow=20
)

def SessionLocal():
    return Session(bind=engine)
