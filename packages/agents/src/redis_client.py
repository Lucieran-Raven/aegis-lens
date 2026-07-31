"""
Redis client for Aegis Agents Service

This module provides Redis integration for caching and pub/sub functionality.
"""

import json
import logging
from typing import Optional, Dict, Any, Callable
import asyncio
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis


class RedisManager:
    """
    Redis connection manager for caching and pub/sub.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
    ):
        """
        Initialize Redis manager.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            decode_responses: Whether to decode responses to strings
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self._client: Optional[Redis] = None
        self._pubsub: Optional[redis.PubSub] = None
        self.logger = logging.getLogger("aegis.agents.redis")

    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._client = await redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
            )
            # Test connection
            await self._client.ping()
            self.logger.info(f"Connected to Redis at {self.host}:{self.port}/{self.db}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        if self._client:
            await self._client.close()
            self._client = None
            self.logger.info("Disconnected from Redis")

    @property
    def client(self) -> Redis:
        """Get Redis client (raises if not connected)."""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    async def cache_result(
        self,
        key: str,
        result: Dict[str, Any],
        ttl_seconds: int = 300,
    ) -> None:
        """
        Cache agent result in Redis.

        Args:
            key: Cache key
            result: Result data to cache
            ttl_seconds: Time-to-live in seconds
        """
        try:
            value = json.dumps(result)
            await self.client.setex(key, ttl_seconds, value)
            self.logger.debug(f"Cached result for key: {key} (TTL: {ttl_seconds}s)")
        except Exception as e:
            self.logger.error(f"Failed to cache result: {str(e)}")

    async def get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result from Redis.

        Args:
            key: Cache key

        Returns:
            Cached result if exists, None otherwise
        """
        try:
            value = await self.client.get(key)
            if value:
                result = json.loads(value)
                self.logger.debug(f"Retrieved cached result for key: {key}")
                return result
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve cached result: {str(e)}")
            return None

    async def delete_cached_result(self, key: str) -> bool:
        """
        Delete cached result from Redis.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.client.delete(key)
            if result:
                self.logger.debug(f"Deleted cached result for key: {key}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete cached result: {str(e)}")
            return False

    async def publish_event(self, channel: str, event: Dict[str, Any]) -> None:
        """
        Publish event to Redis channel.

        Args:
            channel: Channel name
            event: Event data to publish
        """
        try:
            message = json.dumps(event)
            await self.client.publish(channel, message)
            self.logger.debug(f"Published event to channel: {channel}")
        except Exception as e:
            self.logger.error(f"Failed to publish event: {str(e)}")

    async def subscribe(self, channel: str) -> None:
        """
        Subscribe to Redis channel.

        Args:
            channel: Channel name
        """
        try:
            if self._pubsub is None:
                self._pubsub = self.client.pubsub()
            await self._pubsub.subscribe(channel)
            self.logger.info(f"Subscribed to channel: {channel}")
        except Exception as e:
            self.logger.error(f"Failed to subscribe to channel: {str(e)}")
            raise

    async def unsubscribe(self, channel: str) -> None:
        """
        Unsubscribe from Redis channel.

        Args:
            channel: Channel name
        """
        try:
            if self._pubsub:
                await self._pubsub.unsubscribe(channel)
                self.logger.info(f"Unsubscribed from channel: {channel}")
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from channel: {str(e)}")

    async def listen(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Listen for messages on subscribed channels.

        Args:
            callback: Callback function to handle messages
        """
        if self._pubsub is None:
            raise RuntimeError("Not subscribed to any channels. Call subscribe() first.")

        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await callback(data)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse message: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error listening for messages: {str(e)}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get Redis statistics.

        Returns:
            Dictionary with Redis stats
        """
        try:
            info = await self.client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            self.logger.error(f"Failed to get Redis stats: {str(e)}")
            return {}


@asynccontextmanager
async def get_redis_manager(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
) -> RedisManager:
    """
    Context manager for Redis connection.

    Args:
        host: Redis host
        port: Redis port
        db: Redis database number
        password: Redis password (optional)

    Yields:
        RedisManager instance
    """
    manager = RedisManager(host=host, port=port, db=db, password=password)
    await manager.connect()
    try:
        yield manager
    finally:
        await manager.disconnect()
