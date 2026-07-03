from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_size=10, max_overflow=5)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
