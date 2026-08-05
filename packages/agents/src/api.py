"""
FastAPI application for Aegis Agents Service

This module provides the REST API for executing AI agents.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os

from base import BaseAgent, AgentConfig, AgentResult, AgentStatus, AgentPriority
from redis_client import RedisManager


# Pydantic models for API requests/responses
class AgentConfigRequest(BaseModel):
    """Request model for agent configuration"""

    agent_id: str = Field(..., description="Unique identifier for the agent")
    priority: str = Field(
        default="medium", description="Agent priority: low, medium, high, critical"
    )
    timeout_ms: int = Field(default=5000, description="Execution timeout in milliseconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    enable_cache: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")
    log_level: str = Field(default="INFO", description="Logging level")


class AgentExecuteRequest(BaseModel):
    """Request model for agent execution"""

    config: AgentConfigRequest
    input_data: Dict[str, Any] = Field(..., description="Input data for the agent")


class AgentExecuteResponse(BaseModel):
    """Response model for agent execution"""

    agent_id: str
    status: str
    score: float
    confidence: float
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_ms: float
    timestamp: str


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str
    service: str
    version: str
    timestamp: str


class StatsResponse(BaseModel):
    """Response model for agent statistics"""

    agent_id: str
    execution_count: int
    error_count: int
    error_rate: float


# Global agent registry
agent_registry: Dict[str, BaseAgent] = {}
# Global Redis manager
redis_manager: Optional[RedisManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global redis_manager
    # Startup
    logging.info("Starting Aegis Agents Service...")

    # Initialize Redis if enabled
    redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    if redis_enabled:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))
        redis_password = os.getenv("REDIS_PASSWORD")

        try:
            redis_manager = RedisManager(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
            )
            await redis_manager.connect()
            logging.info("Redis connection established")
        except Exception as e:
            logging.warning(f"Failed to connect to Redis: {str(e)}. Running without caching.")
            redis_manager = None
    else:
        logging.info("Redis disabled. Running without caching.")

    yield
    # Shutdown
    logging.info("Shutting down Aegis Agents Service...")
    if redis_manager:
        await redis_manager.disconnect()
        logging.info("Redis connection closed")


# Create FastAPI application
app = FastAPI(
    title="Aegis Agents Service",
    description="REST API for executing AI agents in the Aegis Lens platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the service health status.
    """
    return HealthResponse(
        status="healthy",
        service="aegis-agents",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/execute", response_model=AgentExecuteResponse, tags=["Agents"])
async def execute_agent(request: AgentExecuteRequest):
    """
    Execute an agent with the provided configuration and input data.

    Args:
        request: Agent execution request with config and input data

    Returns:
        Agent execution result

    Raises:
        HTTPException: If agent is not registered or execution fails
    """
    # Convert request config to AgentConfig
    try:
        priority_map = {
            "low": AgentPriority.LOW,
            "medium": AgentPriority.MEDIUM,
            "high": AgentPriority.HIGH,
            "critical": AgentPriority.CRITICAL,
        }
        priority = priority_map.get(request.config.priority.lower(), AgentPriority.MEDIUM)

        config = AgentConfig(
            agent_id=request.config.agent_id,
            priority=priority,
            timeout_ms=request.config.timeout_ms,
            max_retries=request.config.max_retries,
            enable_cache=request.config.enable_cache,
            cache_ttl_seconds=request.config.cache_ttl_seconds,
            log_level=request.config.log_level,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid configuration: {str(e)}"
        )

    # Check if agent is registered
    agent_id = config.agent_id
    if agent_id not in agent_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not registered"
        )

    # Get agent and execute
    agent = agent_registry[agent_id]

    # Check cache if enabled
    cache_key = f"agent:{agent_id}:{hash(str(request.input_data))}"
    if config.enable_cache and redis_manager:
        cached_result = await redis_manager.get_cached_result(cache_key)
        if cached_result:
            logging.info(f"Returning cached result for agent {agent_id}")
            return AgentExecuteResponse(**cached_result)

    try:
        result = agent.execute(request.input_data)

        # Cache result if enabled and successful
        if config.enable_cache and redis_manager and result.status == AgentStatus.COMPLETED:
            result_dict = result.to_dict()
            await redis_manager.cache_result(cache_key, result_dict, config.cache_ttl_seconds)
            logging.info(f"Cached result for agent {agent_id}")

        # Publish event if Redis is available
        if redis_manager:
            event = {
                "agent_id": agent_id,
                "status": result.status.value,
                "score": result.score,
                "timestamp": result.timestamp,
            }
            await redis_manager.publish_event("agent:execution", event)

        return AgentExecuteResponse(
            agent_id=result.agent_id,
            status=result.status.value,
            score=result.score,
            confidence=result.confidence,
            data=result.data,
            metadata=result.metadata,
            error_message=result.error_message,
            execution_time_ms=result.execution_time_ms,
            timestamp=result.timestamp,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}",
        )


@app.get("/agents", tags=["Agents"])
async def list_agents():
    """
    List all registered agents.

    Returns a list of agent IDs that are currently registered.
    """
    return {"agents": list(agent_registry.keys()), "count": len(agent_registry)}


@app.get("/agents/{agent_id}/stats", response_model=StatsResponse, tags=["Agents"])
async def get_agent_stats(agent_id: str):
    """
    Get execution statistics for a specific agent.

    Args:
        agent_id: The agent identifier

    Returns:
        Agent execution statistics

    Raises:
        HTTPException: If agent is not registered
    """
    if agent_id not in agent_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not registered"
        )

    agent = agent_registry[agent_id]
    stats = agent.get_stats()

    return StatsResponse(
        agent_id=stats["agent_id"],
        execution_count=stats["execution_count"],
        error_count=stats["error_count"],
        error_rate=stats["error_rate"],
    )


@app.post("/agents/{agent_id}/reset", tags=["Agents"])
async def reset_agent_stats(agent_id: str):
    """
    Reset execution statistics for a specific agent.

    Args:
        agent_id: The agent identifier

    Returns:
        Confirmation message

    Raises:
        HTTPException: If agent is not registered
    """
    if agent_id not in agent_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not registered"
        )

    agent = agent_registry[agent_id]
    agent.reset_stats()

    return {"message": f"Statistics reset for agent '{agent_id}'", "agent_id": agent_id}


def register_agent(agent: BaseAgent) -> None:
    """
    Register an agent with the service.

    Args:
        agent: The agent instance to register
    """
    agent_id = agent.config.agent_id
    agent_registry[agent_id] = agent
    logging.info(f"Registered agent: {agent_id}")


def unregister_agent(agent_id: str) -> None:
    """
    Unregister an agent from the service.

    Args:
        agent_id: The agent identifier to unregister
    """
    if agent_id in agent_registry:
        del agent_registry[agent_id]
        logging.info(f"Unregistered agent: {agent_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
