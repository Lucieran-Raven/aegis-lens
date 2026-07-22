"""Tests for PostgreSQL setup script"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from setup_postgres import PostgreSQLSetup


class TestPostgreSQLSetup:
    """Test PostgreSQL setup operations"""
    
    @pytest.fixture
    def setup_instance(self):
        """Create PostgreSQLSetup instance"""
        return PostgreSQLSetup(
            host='localhost',
            port=5432,
            user='aegis',
            password='secret',
            database='aegis'
        )
    
    def test_get_connection_url(self, setup_instance):
        """Test connection URL generation"""
        url = setup_instance.get_connection_url()
        assert url == 'postgresql://aegis:secret@localhost:5432/aegis'
    
    def test_connect_success(self, setup_instance):
        """Test successful connection"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.connect()
            
            assert setup_instance.connection == mock_connection
            mock_connect.assert_called_once()
    
    def test_connect_create_db(self, setup_instance):
        """Test connection with create_db flag"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.connect(create_db=True)
            
            mock_connect.assert_called_once_with(
                host='localhost',
                port=5432,
                user='aegis',
                password='secret',
                database='postgres',
                isolation_level=ISOLATION_LEVEL_AUTOCOMMIT
            )
    
    def test_disconnect(self, setup_instance):
        """Test disconnect"""
        mock_connection = Mock()
        setup_instance.connection = mock_connection
        
        setup_instance.disconnect()
        
        mock_connection.close.assert_called_once()
        assert setup_instance.connection is None
    
    def test_create_database_new(self, setup_instance):
        """Test creating new database"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = None  # Database doesn't exist
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            setup_instance.create_database()
            
            mock_cursor.execute.assert_called()
            mock_cursor.execute.assert_any_call(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                ('aegis',)
            )
            mock_cursor.close.assert_called_once()
    
    def test_create_database_exists(self, setup_instance):
        """Test when database already exists"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (1,)  # Database exists
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            setup_instance.create_database()
            
            # Should not try to create database
            calls = [str(call) for call in mock_cursor.execute.call_args_list]
            assert not any('CREATE DATABASE' in call for call in calls)
    
    def test_create_extensions(self, setup_instance):
        """Test creating extensions"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connection.commit = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.create_extensions()
            
            # Should try to create both extensions
            assert mock_cursor.execute.call_count >= 2
            mock_connection.commit.assert_called_once()
    
    def test_verify_setup_success(self, setup_instance):
        """Test successful setup verification"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = ('PostgreSQL 15.0',)
            mock_cursor.fetchall.return_value = [('candidates',), ('sessions',)]
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            result = setup_instance.verify_setup()
            
            assert result is True
            mock_cursor.execute.assert_called()
    
    def test_verify_setup_failure(self, setup_instance):
        """Test setup verification failure"""
        with patch('setup_postgres.psycopg2.connect') as mock_connect:
            mock_connect.side_effect = psycopg2.Error("Connection failed")
            
            result = setup_instance.verify_setup()
            
            assert result is False
    
    def test_run_migrations(self, setup_instance):
        """Test running migrations"""
        with patch('setup_postgres.Config') as mock_config_class:
            with patch('setup_postgres.command.upgrade') as mock_upgrade:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                
                setup_instance.run_migrations('/path/to/alembic.ini')
                
                mock_config.set_main_option.assert_called_with(
                    'sqlalchemy.url',
                    'postgresql://aegis:secret@localhost:5432/aegis'
                )
                mock_upgrade.assert_called_with(mock_config, 'head')
