"""Redis client for AEGIS LENS - Caching and Pub/Sub"""

import json
import logging
from typing import Optional, Any, List, Dict
from redis import Redis as RedisLib, ConnectionPool
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from .config import RedisConfig

logger = logging.getLogger(__name__)


class RedisClient:
    """Production-grade Redis client with caching and pub/sub support"""
    
    def __init__(self, config: RedisConfig):
        """Initialize Redis client with configuration"""
        self.config = config
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[RedisLib] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Redis"""
        try:
            self._pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=self.config.decode_responses,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                max_connections=self.config.max_connections,
            )
            self._client = RedisLib(
                connection_pool=self._pool,
                ssl=self.config.ssl
            )
            self._client.ping()
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def ping(self) -> bool:
        """Check if Redis is responsive"""
        try:
            return self._client.ping() if self._client else False
        except RedisError as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    # Cache operations
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair with optional TTL"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self._client.set(key, value, ex=ttl)
        except RedisError as e:
            logger.error(f"Redis set failed for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            value = self._client.get(key)
            if value is None:
                return None
            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f"Redis get failed for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            return self._client.delete(key) > 0
        except RedisError as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists"""
        try:
            return self._client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis exists failed for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for a key"""
        try:
            return self._client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Redis expire failed for key {key}: {e}")
            return False
    
    # Pub/Sub operations
    def publish(self, channel: str, message: Any) -> int:
        """Publish a message to a channel"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            return self._client.publish(channel, message)
        except RedisError as e:
            logger.error(f"Redis publish failed for channel {channel}: {e}")
            return 0
    
    def subscribe(self, channels: List[str]) -> None:
        """Subscribe to channels (returns pubsub object)"""
        try:
            return self._client.pubsub().subscribe(*channels)
        except RedisError as e:
            logger.error(f"Redis subscribe failed for channels {channels}: {e}")
            raise
    
    # List operations
    def lpush(self, key: str, value: Any) -> int:
        """Push value to left of list"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self._client.lpush(key, value)
        except RedisError as e:
            logger.error(f"Redis lpush failed for key {key}: {e}")
            return 0
    
    def rpush(self, key: str, value: Any) -> int:
        """Push value to right of list"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self._client.rpush(key, value)
        except RedisError as e:
            logger.error(f"Redis rpush failed for key {key}: {e}")
            return 0
    
    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get range of list elements"""
        try:
            values = self._client.lrange(key, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
            return result
        except RedisError as e:
            logger.error(f"Redis lrange failed for key {key}: {e}")
            return []
    
    def llen(self, key: str) -> int:
        """Get list length"""
        try:
            return self._client.llen(key)
        except RedisError as e:
            logger.error(f"Redis llen failed for key {key}: {e}")
            return 0
    
    # Hash operations
    def hset(self, key: str, field: str, value: Any) -> bool:
        """Set field in hash"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self._client.hset(key, field, value) > 0
        except RedisError as e:
            logger.error(f"Redis hset failed for key {key}: {e}")
            return False
    
    def hget(self, key: str, field: str) -> Optional[Any]:
        """Get field from hash"""
        try:
            value = self._client.hget(key, field)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f"Redis hget failed for key {key}: {e}")
            return None
    
    def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all fields from hash"""
        try:
            values = self._client.hgetall(key)
            result = {}
            for field, value in values.items():
                try:
                    result[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field] = value
            return result
        except RedisError as e:
            logger.error(f"Redis hgetall failed for key {key}: {e}")
            return {}
    
    # Set operations
    def sadd(self, key: str, *values: Any) -> int:
        """Add values to set"""
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                else:
                    serialized_values.append(value)
            return self._client.sadd(key, *serialized_values)
        except RedisError as e:
            logger.error(f"Redis sadd failed for key {key}: {e}")
            return 0
    
    def smembers(self, key: str) -> set:
        """Get all members of set"""
        try:
            values = self._client.smembers(key)
            result = set()
            for value in values:
                try:
                    result.add(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.add(value)
            return result
        except RedisError as e:
            logger.error(f"Redis smembers failed for key {key}: {e}")
            return set()
    
    def close(self) -> None:
        """Close Redis connection"""
        if self._pool:
            self._pool.disconnect()
            logger.info("Redis connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
