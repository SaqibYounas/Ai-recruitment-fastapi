from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.settings import settings

get_session = create_async_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
bind=get_session,
class_=AsyncSession,
expire_on_commit=False
)
