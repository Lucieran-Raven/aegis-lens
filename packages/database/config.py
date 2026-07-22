"""
Database configuration and connection management
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """Database configuration"""
    
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "aegis")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "aegis")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "aegis_dev_password")
    
    # TimescaleDB Configuration
    TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
    TIMESCALE_PORT = os.getenv("TIMESCALE_PORT", "5433")
    TIMESCALE_DB = os.getenv("TIMESCALE_DB", "aegis_metrics")
    TIMESCALE_USER = os.getenv("TIMESCALE_USER", "aegis")
    TIMESCALE_PASSWORD = os.getenv("TIMESCALE_PASSWORD", "aegis_dev_password")
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get async PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )
    
    @classmethod
    def get_sync_database_url(cls) -> str:
        """Get sync PostgreSQL connection URL (for Alembic)"""
        return (
            f"postgresql+psycopg2://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )
    
    @classmethod
    def get_timescale_url(cls) -> str:
        """Get async TimescaleDB connection URL"""
        return (
            f"postgresql+asyncpg://{cls.TIMESCALE_USER}:{cls.TIMESCALE_PASSWORD}"
            f"@{cls.TIMESCALE_HOST}:{cls.TIMESCALE_PORT}/{cls.TIMESCALE_DB}"
        )
    
    @classmethod
    def get_sync_timescale_url(cls) -> str:
        """Get sync TimescaleDB connection URL (for Alembic)"""
        return (
            f"postgresql+psycopg2://{cls.TIMESCALE_USER}:{cls.TIMESCALE_PASSWORD}"
            f"@{cls.TIMESCALE_HOST}:{cls.TIMESCALE_PORT}/{cls.TIMESCALE_DB}"
        )


# Async engine
engine = create_async_engine(
    DatabaseConfig.get_database_url(),
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Sync engine for Alembic
sync_engine = None


def get_sync_engine():
    """Get sync database engine for Alembic"""
    global sync_engine
    if sync_engine is None:
        from sqlalchemy import create_engine
        sync_engine = create_engine(
            DatabaseConfig.get_sync_database_url(),
            echo=False,
            pool_pre_ping=True,
        )
    return sync_engine


# TimescaleDB async engine
timescale_engine = None


def get_timescale_engine():
    """Get TimescaleDB async engine"""
    global timescale_engine
    if timescale_engine is None:
        timescale_engine = create_async_engine(
            DatabaseConfig.get_timescale_url(),
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return timescale_engine


# TimescaleDB sync engine for Alembic
timescale_sync_engine = None


def get_timescale_sync_engine():
    """Get TimescaleDB sync engine for Alembic"""
    global timescale_sync_engine
    if timescale_sync_engine is None:
        from sqlalchemy import create_engine
        timescale_sync_engine = create_engine(
            DatabaseConfig.get_sync_timescale_url(),
            echo=False,
            pool_pre_ping=True,
        )
    return timescale_sync_engine
