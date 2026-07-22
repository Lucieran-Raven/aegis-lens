"""TimescaleDB production setup and migration script"""

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


class TimescaleDBSetup:
    """Production TimescaleDB setup and migration manager"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Initialize TimescaleDB setup"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self, create_db: bool = False) -> None:
        """Connect to TimescaleDB server"""
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
            logger.info(f"Connected to TimescaleDB at {self.host}:{self.port}")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close TimescaleDB connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("TimescaleDB connection closed")
    
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
    
    def enable_timescale(self) -> None:
        """Enable TimescaleDB extension"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Enable TimescaleDB extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
            logger.info("TimescaleDB extension enabled")
            
            self.connection.commit()
            cursor.close()
        except psycopg2.Error as e:
            logger.error(f"Failed to enable TimescaleDB extension: {e}")
            raise
        finally:
            self.disconnect()
    
    def create_hypertable(self, table_name: str, time_column: str) -> None:
        """Convert a table to a hypertable for time-series data"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Check if table exists
            cursor.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = %s AND table_schema = 'public'",
                (table_name,)
            )
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Check if already a hypertable
                cursor.execute(
                    "SELECT 1 FROM timescaledb_information.hypertables "
                    "WHERE hypertable_name = %s",
                    (table_name,)
                )
                is_hypertable = cursor.fetchone()
                
                if not is_hypertable:
                    cursor.execute(
                        f"SELECT create_hypertable('{table_name}', '{time_column}')"
                    )
                    logger.info(f"Table '{table_name}' converted to hypertable")
                else:
                    logger.info(f"Table '{table_name}' is already a hypertable")
            else:
                logger.warning(f"Table '{table_name}' does not exist")
            
            self.connection.commit()
            cursor.close()
        except psycopg2.Error as e:
            logger.error(f"Failed to create hypertable: {e}")
            raise
        finally:
            self.disconnect()
    
    def create_retention_policy(self, table_name: str, interval: str) -> None:
        """Create a data retention policy for a hypertable"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Add retention policy
            cursor.execute(
                f"SELECT add_retention_policy('{table_name}', INTERVAL '{interval}')"
            )
            logger.info(f"Retention policy created for '{table_name}': {interval}")
            
            self.connection.commit()
            cursor.close()
        except psycopg2.Error as e:
            logger.error(f"Failed to create retention policy: {e}")
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
        """Get TimescaleDB connection URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def verify_setup(self) -> bool:
        """Verify TimescaleDB setup is working"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Check TimescaleDB version
            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'")
            version = cursor.fetchone()
            if version:
                logger.info(f"TimescaleDB version: {version[0]}")
            else:
                logger.warning("TimescaleDB extension not found")
            
            # Check hypertables
            cursor.execute("SELECT hypertable_name FROM timescaledb_information.hypertables")
            hypertables = cursor.fetchall()
            logger.info(f"Hypertables: {[h[0] for h in hypertables]}")
            
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
    host = os.getenv('TIMESCALE_HOST', 'localhost')
    port = int(os.getenv('TIMESCALE_PORT', '5433'))
    user = os.getenv('TIMESCALE_USER', 'aegis')
    password = os.getenv('TIMESCALE_PASSWORD', 'aegis_dev_password')
    database = os.getenv('TIMESCALE_DATABASE', 'aegis_metrics')
    
    # Path to Alembic config
    script_dir = Path(__file__).parent
    alembic_ini = script_dir / 'alembic_timescale.ini'
    
    logger.info("Starting TimescaleDB production setup...")
    
    setup = TimescaleDBSetup(host, port, user, password, database)
    
    try:
        # Step 1: Create database
        setup.create_database()
        
        # Step 2: Enable TimescaleDB extension
        setup.enable_timescale()
        
        # Step 3: Run migrations
        if alembic_ini.exists():
            setup.run_migrations(str(alembic_ini))
        else:
            logger.warning(f"Alembic config not found at {alembic_ini}")
        
        # Step 4: Verify setup
        if setup.verify_setup():
            logger.info("TimescaleDB setup completed successfully!")
            return 0
        else:
            logger.error("TimescaleDB setup verification failed")
            return 1
            
    except Exception as e:
        logger.error(f"TimescaleDB setup failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
