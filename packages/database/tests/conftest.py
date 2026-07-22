"""
Pytest configuration and fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models.base import Base


@pytest.fixture(scope="function")
def db_engine():
    """Create sync test engine"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(engine)
    
    yield engine
    
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create sync test session"""
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    
    session = SessionLocal()
    
    yield session
    
    session.close()
