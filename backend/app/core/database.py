"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine
try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,  # Enable connection health checks
    )
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info("Database connection established successfully")
    DB_CONNECTED = True
except Exception as e:
    logger.warning(f"Database connection failed: {e}. Running without database.")
    engine = None
    DB_CONNECTED = False

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Optional[Session], None, None]:
    """
    Dependency to get database session
    """
    if not DB_CONNECTED or not SessionLocal:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
