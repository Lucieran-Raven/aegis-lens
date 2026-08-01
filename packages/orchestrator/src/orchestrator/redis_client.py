"""
Redis Client for Orchestrator

This module provides Redis integration for caching verdicts and recommendations,
as well as pub/sub functionality for real-time updates.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from datetime import datetime, timezone


class OrchestratorRedisManager:
    """
    Redis manager for orchestrator caching and pub/sub.

    Provides methods for caching verdicts, recommendations, and
    publishing events for real-time updates.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 10,
    ):
        """
        Initialize Redis manager.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            max_connections: Maximum connection pool size
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections

        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Establish Redis connection pool"""
        try:
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=True,
            )
            self._client = redis.Redis(connection_pool=self._pool)

            # Test connection
            await self._client.ping()
            self.logger.info(f"Connected to Redis at {self.host}:{self.port}/{self.db}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection pool"""
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
            self._client = None
            self.logger.info("Disconnected from Redis")

    @property
    def client(self) -> redis.Redis:
        """Get Redis client (raises error if not connected)"""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    @asynccontextmanager
    async def get_client(self):
        """Context manager for Redis client"""
        if self._client is None:
            await self.connect()
        try:
            yield self.client
        finally:
            pass

    async def cache_verdict(
        self,
        session_id: str,
        verdict: Dict[str, Any],
        ttl_seconds: int = 3600,
    ) -> bool:
        """
        Cache a verdict for a session.

        Args:
            session_id: Session identifier
            verdict: Verdict data dictionary
            ttl_seconds: Time to live in seconds

        Returns:
            True if cached successfully
        """
        try:
            key = f"verdict:{session_id}"
            value = json.dumps(verdict)
            await self.client.setex(key, ttl_seconds, value)
            self.logger.info(f"Cached verdict for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache verdict: {e}")
            return False

    async def get_cached_verdict(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached verdict for a session.

        Args:
            session_id: Session identifier

        Returns:
            Verdict data or None if not found
        """
        try:
            key = f"verdict:{session_id}"
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cached verdict: {e}")
            return None

    async def cache_recommendation(
        self,
        session_id: str,
        recommendation: Dict[str, Any],
        ttl_seconds: int = 3600,
    ) -> bool:
        """
        Cache recommendations for a session.

        Args:
            session_id: Session identifier
            recommendation: Recommendation data dictionary
            ttl_seconds: Time to live in seconds

        Returns:
            True if cached successfully
        """
        try:
            key = f"recommendation:{session_id}"
            value = json.dumps(recommendation)
            await self.client.setex(key, ttl_seconds, value)
            self.logger.info(f"Cached recommendation for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache recommendation: {e}")
            return False

    async def get_cached_recommendation(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached recommendation for a session.

        Args:
            session_id: Session identifier

        Returns:
            Recommendation data or None if not found
        """
        try:
            key = f"recommendation:{session_id}"
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cached recommendation: {e}")
            return None

    async def cache_agent_results(
        self,
        session_id: str,
        agent_results: List[Dict[str, Any]],
        ttl_seconds: int = 1800,
    ) -> bool:
        """
        Cache agent results for a session.

        Args:
            session_id: Session identifier
            agent_results: List of agent result dictionaries
            ttl_seconds: Time to live in seconds

        Returns:
            True if cached successfully
        """
        try:
            key = f"agent_results:{session_id}"
            value = json.dumps(agent_results)
            await self.client.setex(key, ttl_seconds, value)
            self.logger.info(f"Cached agent results for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache agent results: {e}")
            return False

    async def get_cached_agent_results(
        self, session_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached agent results for a session.

        Args:
            session_id: Session identifier

        Returns:
            Agent results list or None if not found
        """
        try:
            key = f"agent_results:{session_id}"
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cached agent results: {e}")
            return None

    async def store_trust_history(
        self,
        session_id: str,
        trust_score: float,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Store trust score in session history.

        Args:
            session_id: Session identifier
            trust_score: Trust score value
            timestamp: Timestamp (defaults to now)

        Returns:
            True if stored successfully
        """
        try:
            key = f"trust_history:{session_id}"
            ts = timestamp or datetime.now(timezone.utc)
            value = json.dumps(
                {"score": trust_score, "timestamp": ts.isoformat()}
            )
            await self.client.lpush(key, value)
            # Keep last 100 entries
            await self.client.ltrim(key, 0, 99)
            # Set expiry
            await self.client.expire(key, 86400)  # 24 hours
            self.logger.debug(f"Stored trust score {trust_score} for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store trust history: {e}")
            return False

    async def get_trust_history(
        self, session_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve trust score history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of entries to retrieve

        Returns:
            List of trust score entries
        """
        try:
            key = f"trust_history:{session_id}"
            values = await self.client.lrange(key, 0, limit - 1)
            return [json.loads(v) for v in values]
        except Exception as e:
            self.logger.error(f"Failed to get trust history: {e}")
            return []

    async def publish_verdict_event(
        self, session_id: str, verdict: Dict[str, Any]
    ) -> bool:
        """
        Publish verdict event to pub/sub channel.

        Args:
            session_id: Session identifier
            verdict: Verdict data

        Returns:
            True if published successfully
        """
        try:
            channel = f"verdict:{session_id}"
            message = json.dumps(
                {"type": "verdict", "session_id": session_id, "data": verdict}
            )
            await self.client.publish(channel, message)
            self.logger.info(f"Published verdict event for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish verdict event: {e}")
            return False

    async def publish_recommendation_event(
        self, session_id: str, recommendation: Dict[str, Any]
    ) -> bool:
        """
        Publish recommendation event to pub/sub channel.

        Args:
            session_id: Session identifier
            recommendation: Recommendation data

        Returns:
            True if published successfully
        """
        try:
            channel = f"recommendation:{session_id}"
            message = json.dumps(
                {"type": "recommendation", "session_id": session_id, "data": recommendation}
            )
            await self.client.publish(channel, message)
            self.logger.info(
                f"Published recommendation event for session {session_id}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish recommendation event: {e}")
            return False

    async def subscribe_to_verdict(self, session_id: str):
        """
        Subscribe to verdict events for a session.

        Args:
            session_id: Session identifier

        Returns:
            PubSub object
        """
        try:
            channel = f"verdict:{session_id}"
            pubsub = self.client.pubsub()
            await pubsub.subscribe(channel)
            self.logger.info(f"Subscribed to verdict channel for session {session_id}")
            return pubsub
        except Exception as e:
            self.logger.error(f"Failed to subscribe to verdict channel: {e}")
            raise

    async def delete_session_data(self, session_id: str) -> bool:
        """
        Delete all cached data for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        try:
            keys = [
                f"verdict:{session_id}",
                f"recommendation:{session_id}",
                f"agent_results:{session_id}",
                f"trust_history:{session_id}",
            ]
            await self.client.delete(*keys)
            self.logger.info(f"Deleted session data for {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete session data: {e}")
            return False

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
                "used_memory": info.get("used_memory_human", "0B"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            self.logger.error(f"Failed to get Redis stats: {e}")
            return {}

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
