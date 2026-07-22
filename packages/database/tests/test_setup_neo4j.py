"""Tests for Neo4j setup script"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from neo4j.exceptions import ServiceUnavailable, AuthError

from setup_neo4j import Neo4jSetup


class TestNeo4jSetup:
    """Test Neo4j setup operations"""
    
    @pytest.fixture
    def setup_instance(self):
        """Create Neo4jSetup instance"""
        return Neo4jSetup(
            uri='bolt://localhost:7687',
            user='neo4j',
            password='secret'
        )
    
    def test_connect_success(self, setup_instance):
        """Test successful connection"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver = Mock()
            mock_driver.verify_connectivity = Mock()
            mock_driver_class.return_value = mock_driver
            
            setup_instance.connect()
            
            assert setup_instance.driver == mock_driver
            mock_driver_class.assert_called_once_with(
                'bolt://localhost:7687',
                auth=('neo4j', 'secret')
            )
            mock_driver.verify_connectivity.assert_called_once()
    
    def test_connect_failure(self, setup_instance):
        """Test connection failure"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver_class.side_effect = ServiceUnavailable("Connection failed")
            
            with pytest.raises(ServiceUnavailable):
                setup_instance.connect()
    
    def test_disconnect(self, setup_instance):
        """Test disconnect"""
        mock_driver = Mock()
        setup_instance.driver = mock_driver
        
        setup_instance.disconnect()
        
        mock_driver.close.assert_called_once()
        assert setup_instance.driver is None
    
    def test_create_constraints(self, setup_instance):
        """Test creating constraints"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver = Mock()
            mock_session = Mock()
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)
            mock_driver.verify_connectivity = Mock()
            mock_driver_class.return_value = mock_driver
            
            setup_instance.create_constraints()
            
            # Should have run constraint creation queries
            assert mock_session.run.call_count >= 5
    
    def test_create_indexes(self, setup_instance):
        """Test creating indexes"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver = Mock()
            mock_session = Mock()
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)
            mock_driver.verify_connectivity = Mock()
            mock_driver_class.return_value = mock_driver
            
            setup_instance.create_indexes()
            
            # Should have run index creation queries
            assert mock_session.run.call_count >= 5
    
    def test_initialize_schema(self, setup_instance):
        """Test schema initialization"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver = Mock()
            mock_session = Mock()
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)
            mock_driver.verify_connectivity = Mock()
            mock_driver_class.return_value = mock_driver
            
            setup_instance.initialize_schema()
            
            mock_session.run.assert_called()
    
    def test_verify_setup_success(self, setup_instance):
        """Test successful setup verification"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver = Mock()
            mock_session = Mock()
            mock_result = Mock()
            mock_result.__iter__ = Mock(return_value=iter([
                {'name': 'Neo4j', 'version': '5.0.0', 'edition': 'Enterprise'}
            ]))
            mock_session.run.return_value = mock_result
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)
            mock_driver.verify_connectivity = Mock()
            mock_driver_class.return_value = mock_driver
            
            result = setup_instance.verify_setup()
            
            assert result is True
    
    def test_verify_setup_failure(self, setup_instance):
        """Test setup verification failure"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver_class.side_effect = ServiceUnavailable("Connection failed")
            
            result = setup_instance.verify_setup()
            
            assert result is False
    
    def test_clear_database(self, setup_instance):
        """Test clearing database"""
        with patch('setup_neo4j.GraphDatabase.driver') as mock_driver_class:
            mock_driver = Mock()
            mock_session = Mock()
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)
            mock_driver.verify_connectivity = Mock()
            mock_driver_class.return_value = mock_driver
            
            setup_instance.clear_database()
            
            mock_session.run.assert_called_with("MATCH (n) DETACH DELETE n")
