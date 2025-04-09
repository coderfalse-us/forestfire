"""
SQLAlchemy ORM base configuration.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator, Any
import logging

# Load environment variables
load_dotenv()

# Create logger
logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))

# Create connection string
CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(
    CONNECTION_STRING,
    pool_size=DB_POOL_SIZE,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Check connection before using it
    echo=False  # Set to True for SQL logging
)

# Create session factory
SessionFactory = sessionmaker(bind=engine)
ScopedSession = scoped_session(SessionFactory)

# Read-only session factory
ReadOnlySessionFactory = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
ReadOnlyScopedSession = scoped_session(ReadOnlySessionFactory)


@contextmanager
def get_db_session(read_only: bool = False) -> Generator[Any, None, None]:
    """
    Context manager for database sessions.
    
    Args:
        read_only: If True, creates a read-only session
        
    Yields:
        SQLAlchemy session
    """
    if read_only:
        session = ReadOnlyScopedSession()
        # Make the session read-only by setting expire_on_commit to False
        # and making autoflush and autocommit False
        session.expire_on_commit = False
        try:
            yield session
            # For read-only sessions, we don't commit, just close
        except Exception as e:
            logger.error(f"Error in read-only database session: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            ReadOnlyScopedSession.remove()
    else:
        session = ScopedSession()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Error in database session: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            ScopedSession.remove()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Only use this for development or testing.
    """
    Base.metadata.create_all(engine)


def drop_db() -> None:
    """
    Drop all tables from the database.
    Only use this for development or testing.
    """
    Base.metadata.drop_all(engine)
