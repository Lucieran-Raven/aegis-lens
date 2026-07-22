"""Tests for TimescaleDB setup script"""

import pytest
from unittest.mock import Mock, patch
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from setup_timescale import TimescaleDBSetup


class TestTimescaleDBSetup:
    """Test TimescaleDB setup operations"""
    
    @pytest.fixture
    def setup_instance(self):
        """Create TimescaleDBSetup instance"""
        return TimescaleDBSetup(
            host='localhost',
            port=5433,
            user='aegis',
            password='secret',
            database='aegis_metrics'
        )
    
    def test_get_connection_url(self, setup_instance):
        """Test connection URL generation"""
        url = setup_instance.get_connection_url()
        assert url == 'postgresql://aegis:secret@localhost:5433/aegis_metrics'
    
    def test_connect_success(self, setup_instance):
        """Test successful connection"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.connect()
            
            assert setup_instance.connection == mock_connection
            mock_connect.assert_called_once()
    
    def test_connect_create_db(self, setup_instance):
        """Test connection with create_db flag"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.connect(create_db=True)
            
            mock_connect.assert_called_once_with(
                host='localhost',
                port=5433,
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
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = None  # Database doesn't exist
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            setup_instance.create_database()
            
            mock_cursor.execute.assert_called()
            mock_cursor.execute.assert_any_call(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                ('aegis_metrics',)
            )
            mock_cursor.close.assert_called_once()
    
    def test_create_database_exists(self, setup_instance):
        """Test when database already exists"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (1,)  # Database exists
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            setup_instance.create_database()
            
            # Should not try to create database
            calls = [str(call) for call in mock_cursor.execute.call_args_list]
            assert not any('CREATE DATABASE' in call for call in calls)
    
    def test_enable_timescale(self, setup_instance):
        """Test enabling TimescaleDB extension"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connection.commit = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.enable_timescale()
            
            mock_cursor.execute.assert_called_with(
                "CREATE EXTENSION IF NOT EXISTS timescaledb"
            )
            mock_connection.commit.assert_called_once()
    
    def test_create_hypertable(self, setup_instance):
        """Test creating hypertable"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (1,)  # Table exists
            mock_connection.cursor.return_value = mock_cursor
            mock_connection.commit = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.create_hypertable('metrics', 'timestamp')
            
            mock_cursor.execute.assert_called()
            mock_connection.commit.assert_called_once()
    
    def test_create_retention_policy(self, setup_instance):
        """Test creating retention policy"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connection.commit = Mock()
            mock_connect.return_value = mock_connection
            
            setup_instance.create_retention_policy('metrics', '30 days')
            
            mock_cursor.execute.assert_called()
            mock_connection.commit.assert_called_once()
    
    def test_verify_setup_success(self, setup_instance):
        """Test successful setup verification"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = ('2.12.0',)
            mock_cursor.fetchall.return_value = [('metrics',)]
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            result = setup_instance.verify_setup()
            
            assert result is True
            mock_cursor.execute.assert_called()
    
    def test_verify_setup_failure(self, setup_instance):
        """Test setup verification failure"""
        with patch('setup_timescale.psycopg2.connect') as mock_connect:
            mock_connect.side_effect = psycopg2.Error("Connection failed")
            
            result = setup_instance.verify_setup()
            
            assert result is False
    
    def test_run_migrations(self, setup_instance):
        """Test running migrations"""
        with patch('setup_timescale.Config') as mock_config_class:
            with patch('setup_timescale.command.upgrade') as mock_upgrade:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                
                setup_instance.run_migrations('/path/to/alembic.ini')
                
                mock_config.set_main_option.assert_called_with(
                    'sqlalchemy.url',
                    'postgresql://aegis:secret@localhost:5433/aegis_metrics'
                )
                mock_upgrade.assert_called_with(mock_config, 'head')
