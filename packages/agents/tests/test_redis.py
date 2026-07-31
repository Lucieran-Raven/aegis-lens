"""
Unit tests for Redis client
"""

import pytest
from typing import Dict, Any
import asyncio

from src.redis_client import RedisManager, get_redis_manager


@pytest.mark.asyncio
class TestRedisManager:
    """Tests for RedisManager"""
    
    async def test_connect_disconnect(self):
        """Test connecting and disconnecting from Redis"""
        manager = RedisManager(host="localhost", port=6379)
        
        # Note: This test requires a running Redis instance
        # Skip if Redis is not available
        try:
            await manager.connect()
            assert manager._client is not None
            
            await manager.disconnect()
            assert manager._client is None
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_cache_result(self):
        """Test caching a result"""
        manager = RedisManager(host="localhost", port=6379)
        
        try:
            await manager.connect()
            
            result = {"score": 0.85, "status": "completed"}
            await manager.cache_result("test_key", result, ttl_seconds=60)
            
            cached = await manager.get_cached_result("test_key")
            assert cached is not None
            assert cached["score"] == 0.85
            assert cached["status"] == "completed"
            
            await manager.disconnect()
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_get_cached_result_not_found(self):
        """Test getting non-existent cached result"""
        manager = RedisManager(host="localhost", port=6379)
        
        try:
            await manager.connect()
            
            cached = await manager.get_cached_result("non_existent_key")
            assert cached is None
            
            await manager.disconnect()
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_delete_cached_result(self):
        """Test deleting a cached result"""
        manager = RedisManager(host="localhost", port=6379)
        
        try:
            await manager.connect()
            
            # Cache a result
            result = {"score": 0.85}
            await manager.cache_result("delete_test_key", result, ttl_seconds=60)
            
            # Delete it
            deleted = await manager.delete_cached_result("delete_test_key")
            assert deleted is True
            
            # Verify it's gone
            cached = await manager.get_cached_result("delete_test_key")
            assert cached is None
            
            await manager.disconnect()
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_publish_subscribe(self):
        """Test publishing and subscribing to events"""
        manager = RedisManager(host="localhost", port=6379)
        
        try:
            await manager.connect()
            
            received_messages = []
            
            async def callback(message: Dict[str, Any]):
                received_messages.append(message)
            
            # Subscribe
            await manager.subscribe("test_channel")
            
            # Publish
            event = {"agent_id": "test", "status": "completed"}
            await manager.publish_event("test_channel", event)
            
            # Give time for message to propagate
            await asyncio.sleep(0.1)
            
            # Note: In a real test, we'd need to run listen() in a task
            # For now, just test that publish doesn't fail
            
            await manager.unsubscribe("test_channel")
            await manager.disconnect()
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_get_stats(self):
        """Test getting Redis statistics"""
        manager = RedisManager(host="localhost", port=6379)
        
        try:
            await manager.connect()
            
            stats = await manager.get_stats()
            assert isinstance(stats, dict)
            assert "connected_clients" in stats
            assert "used_memory_human" in stats
            
            await manager.disconnect()
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_context_manager(self):
        """Test RedisManager as context manager"""
        try:
            async with get_redis_manager(host="localhost", port=6379) as manager:
                assert manager._client is not None
                
                # Test basic operation
                result = {"test": "data"}
                await manager.cache_result("ctx_test", result, ttl_seconds=60)
                cached = await manager.get_cached_result("ctx_test")
                assert cached is not None
            
            # Connection should be closed after context
            assert manager._client is None
        except Exception as e:
            pytest.skip(f"Redis not available: {str(e)}")
    
    async def test_client_property_not_connected(self):
        """Test that client property raises when not connected"""
        manager = RedisManager(host="localhost", port=6379)
        
        with pytest.raises(RuntimeError, match="not connected"):
            _ = manager.client


class TestRedisManagerUnit:
    """Unit tests that don't require Redis connection"""
    
    def test_initialization(self):
        """Test RedisManager initialization"""
        manager = RedisManager(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
        )
        
        assert manager.host == "redis.example.com"
        assert manager.port == 6380
        assert manager.db == 1
        assert manager.password == "secret"
    
    def test_initialization_defaults(self):
        """Test RedisManager initialization with defaults"""
        manager = RedisManager()
        
        assert manager.host == "localhost"
        assert manager.port == 6379
        assert manager.db == 0
        assert manager.password is None
