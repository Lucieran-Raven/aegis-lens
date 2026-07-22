"""Tests for Redis client"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from redis.exceptions import ConnectionError, TimeoutError

from redis import Redis as RedisLibClient
from redis import ConnectionPool

from ..client import RedisClient
from ..config import RedisConfig


class TestRedisConfig:
    """Test Redis configuration"""
    
    def test_from_env_defaults(self):
        """Test configuration from environment with defaults"""
        config = RedisConfig.from_env()
        assert config.host == 'localhost'
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.ssl is False
        assert config.decode_responses is True
    
    def test_from_env_custom(self, monkeypatch):
        """Test configuration from environment with custom values"""
        monkeypatch.setenv('REDIS_HOST', 'custom-host')
        monkeypatch.setenv('REDIS_PORT', '6380')
        monkeypatch.setenv('REDIS_DB', '1')
        monkeypatch.setenv('REDIS_PASSWORD', 'secret')
        monkeypatch.setenv('REDIS_SSL', 'true')
        
        config = RedisConfig.from_env()
        assert config.host == 'custom-host'
        assert config.port == 6380
        assert config.db == 1
        assert config.password == 'secret'
        assert config.ssl is True
    
    def test_from_docker(self):
        """Test Docker configuration"""
        config = RedisConfig.from_docker()
        assert config.host == 'redis'
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.ssl is False
    
    def test_to_url_without_password(self):
        """Test URL generation without password"""
        config = RedisConfig(host='localhost', port=6379, db=0, password=None,
                           ssl=False, decode_responses=True, socket_timeout=5,
                           socket_connect_timeout=5, max_connections=50)
        assert config.to_url() == 'redis://localhost:6379/0'
    
    def test_to_url_with_password(self):
        """Test URL generation with password"""
        config = RedisConfig(host='localhost', port=6379, db=0, password='secret',
                           ssl=False, decode_responses=True, socket_timeout=5,
                           socket_connect_timeout=5, max_connections=50)
        assert config.to_url() == 'redis://:secret@localhost:6379/0'


class TestRedisClient:
    """Test Redis client operations"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return RedisConfig(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            ssl=False,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            max_connections=50,
        )
    
    @pytest.fixture
    def mock_client(self, config):
        """Create Redis client with mocked connection"""
        with patch('database.redis.client.ConnectionPool') as mock_pool_class:
            with patch('database.redis.client.RedisLib') as mock_redis_class:
                mock_pool = Mock()
                mock_pool_class.return_value = mock_pool
                
                mock_redis = Mock()
                mock_redis.ping.return_value = True
                mock_redis.set.return_value = True
                mock_redis.get.return_value = 'value'
                mock_redis.delete.return_value = 1
                mock_redis.exists.return_value = 1
                mock_redis.expire.return_value = True
                mock_redis.publish.return_value = 1
                mock_redis.lpush.return_value = 1
                mock_redis.rpush.return_value = 1
                mock_redis.lrange.return_value = ['value1', 'value2']
                mock_redis.llen.return_value = 2
                mock_redis.hset.return_value = 1
                mock_redis.hget.return_value = 'field_value'
                mock_redis.hgetall.return_value = {'field': 'value'}
                mock_redis.sadd.return_value = 1
                mock_redis.smembers.return_value = {'member1', 'member2'}
                
                mock_redis_class.return_value = mock_redis
                client = RedisClient(config)
                yield client, mock_redis
    
    def test_connect_success(self, mock_client):
        """Test successful connection"""
        client, _ = mock_client
        assert client.ping() is True
    
    def test_connect_failure(self, config):
        """Test connection failure"""
        with patch('database.redis.client.ConnectionPool') as mock_pool:
            mock_pool.side_effect = ConnectionError("Connection failed")
            with pytest.raises(ConnectionError):
                RedisClient(config)
    
    def test_ping(self, mock_client):
        """Test ping operation"""
        client, _ = mock_client
        assert client.ping() is True
    
    def test_set_get_string(self, mock_client):
        """Test set and get string values"""
        client, mock_redis = mock_client
        client.set('key', 'value')
        result = client.get('key')
        assert result == 'value'
    
    def test_set_get_json(self, mock_client):
        """Test set and get JSON values"""
        client, mock_redis = mock_client
        test_data = {'key': 'value', 'number': 42}
        client.set('key', test_data)
        mock_redis.get.return_value = json.dumps(test_data)
        result = client.get('key')
        assert result == test_data
    
    def test_delete(self, mock_client):
        """Test delete operation"""
        client, _ = mock_client
        assert client.delete('key') is True
    
    def test_exists(self, mock_client):
        """Test exists operation"""
        client, _ = mock_client
        assert client.exists('key') is True
    
    def test_expire(self, mock_client):
        """Test expire operation"""
        client, _ = mock_client
        assert client.expire('key', 60) is True
    
    def test_publish(self, mock_client):
        """Test publish operation"""
        client, _ = mock_client
        assert client.publish('channel', 'message') == 1
    
    def test_lpush_rpush(self, mock_client):
        """Test list push operations"""
        client, _ = mock_client
        assert client.lpush('list', 'value') == 1
        assert client.rpush('list', 'value') == 1
    
    def test_lrange(self, mock_client):
        """Test list range operation"""
        client, _ = mock_client
        result = client.lrange('list', 0, -1)
        assert result == ['value1', 'value2']
    
    def test_llen(self, mock_client):
        """Test list length operation"""
        client, _ = mock_client
        assert client.llen('list') == 2
    
    def test_hset_hget(self, mock_client):
        """Test hash set and get operations"""
        client, _ = mock_client
        assert client.hset('hash', 'field', 'value') is True
        assert client.hget('hash', 'field') == 'field_value'
    
    def test_hgetall(self, mock_client):
        """Test hash get all operation"""
        client, _ = mock_client
        result = client.hgetall('hash')
        assert result == {'field': 'value'}
    
    def test_sadd_smembers(self, mock_client):
        """Test set add and members operations"""
        client, _ = mock_client
        assert client.sadd('set', 'member1') == 1
        result = client.smembers('set')
        assert result == {'member1', 'member2'}
    
    def test_context_manager(self, config):
        """Test context manager"""
        with patch('database.redis.client.ConnectionPool') as mock_pool_class:
            with patch('database.redis.client.RedisLib') as mock_redis_class:
                mock_pool = Mock()
                mock_pool_class.return_value = mock_pool
                
                mock_redis = Mock()
                mock_redis.ping.return_value = True
                mock_redis_class.return_value = mock_redis
                
                with RedisClient(config) as client:
                    assert client.ping() is True
                mock_pool.disconnect.assert_called_once()
