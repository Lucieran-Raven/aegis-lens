"""PostgreSQL production setup and migration script"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLSetup:
    """Production PostgreSQL setup and migration manager"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Initialize PostgreSQL setup"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self, create_db: bool = False) -> None:
        """Connect to PostgreSQL server"""
        try:
            if create_db:
                # Connect to postgres database to create new database
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database='postgres',
                    isolation_level=ISOLATION_LEVEL_AUTOCOMMIT
                )
            else:
                # Connect to target database
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("PostgreSQL connection closed")
    
    def create_database(self) -> None:
        """Create the database if it doesn't exist"""
        try:
            self.connect(create_db=True)
            cursor = self.connection.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.database,)
            )
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(
                    f"CREATE DATABASE {self.database} "
                    f"ENCODING 'UTF8' "
                    f"LC_COLLATE='en_US.UTF-8' "
                    f"LC_CTYPE='en_US.UTF-8'"
                )
                logger.info(f"Database '{self.database}' created")
            else:
                logger.info(f"Database '{self.database}' already exists")
            
            cursor.close()
        except psycopg2.Error as e:
            logger.error(f"Failed to create database: {e}")
            raise
        finally:
            self.disconnect()
    
    def create_extensions(self) -> None:
        """Create required PostgreSQL extensions"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            extensions = ['uuid-ossp', 'pgcrypto']
            
            for ext in extensions:
                try:
                    cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
                    logger.info(f"Extension '{ext}' created/verified")
                except psycopg2.Error as e:
                    logger.warning(f"Failed to create extension '{ext}': {e}")
            
            self.connection.commit()
            cursor.close()
        except psycopg2.Error as e:
            logger.error(f"Failed to create extensions: {e}")
            raise
        finally:
            self.disconnect()
    
    def run_migrations(self, alembic_ini_path: str) -> None:
        """Run Alembic migrations"""
        try:
            config = Config(alembic_ini_path)
            config.set_main_option('sqlalchemy.url', self.get_connection_url())
            
            # Upgrade to latest
            command.upgrade(config, 'head')
            logger.info("Migrations completed successfully")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def get_connection_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def verify_setup(self) -> bool:
        """Verify PostgreSQL setup is working"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Test basic query
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            logger.info(f"PostgreSQL version: {version[0]}")
            
            # Check tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            logger.info(f"Tables in database: {[t[0] for t in tables]}")
            
            cursor.close()
            return True
        except psycopg2.Error as e:
            logger.error(f"Setup verification failed: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main setup function"""
    # Get configuration from environment
    host = os.getenv('PG_HOST', 'localhost')
    port = int(os.getenv('PG_PORT', '5432'))
    user = os.getenv('PG_USER', 'aegis')
    password = os.getenv('PG_PASSWORD', 'aegis_dev_password')
    database = os.getenv('PG_DATABASE', 'aegis')
    
    # Path to Alembic config
    script_dir = Path(__file__).parent
    alembic_ini = script_dir / 'alembic.ini'
    
    logger.info("Starting PostgreSQL production setup...")
    
    setup = PostgreSQLSetup(host, port, user, password, database)
    
    try:
        # Step 1: Create database
        setup.create_database()
        
        # Step 2: Create extensions
        setup.create_extensions()
        
        # Step 3: Run migrations
        if alembic_ini.exists():
            setup.run_migrations(str(alembic_ini))
        else:
            logger.warning(f"Alembic config not found at {alembic_ini}")
        
        # Step 4: Verify setup
        if setup.verify_setup():
            logger.info("PostgreSQL setup completed successfully!")
            return 0
        else:
            logger.error("PostgreSQL setup verification failed")
            return 1
            
    except Exception as e:
        logger.error(f"PostgreSQL setup failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
