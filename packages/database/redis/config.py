"""Redis configuration for AEGIS LENS"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class RedisConfig:
    """Redis connection configuration"""
    
    host: str
    port: int
    db: int
    password: Optional[str]
    ssl: bool
    decode_responses: bool
    socket_timeout: int
    socket_connect_timeout: int
    max_connections: int
    
    @classmethod
    def from_env(cls) -> 'RedisConfig':
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_SSL', 'false').lower() == 'true',
            decode_responses=True,
            socket_timeout=int(os.getenv('REDIS_SOCKET_TIMEOUT', '5')),
            socket_connect_timeout=int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', '5')),
            max_connections=int(os.getenv('REDIS_MAX_CONNECTIONS', '50')),
        )
    
    @classmethod
    def from_docker(cls) -> 'RedisConfig':
        """Create configuration for Docker environment"""
        return cls(
            host='redis',
            port=6379,
            db=0,
            password=None,
            ssl=False,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            max_connections=50,
        )
    
    def to_url(self) -> str:
        """Convert to Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
