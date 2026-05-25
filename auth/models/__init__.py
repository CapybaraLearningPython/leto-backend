from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import settings

engine = create_async_engine(
    url=settings.DB_URI,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=10,
    pool_recycle=3600,
    pool_pre_ping=True, 
)

AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=True,
    expire_on_commit=True
)

Base = declarative_base()

from . import user