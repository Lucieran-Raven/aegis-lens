"""
Base Agent Abstract Class for Aegis Lens AI Agents

This module provides the foundation for all AI agents in the Aegis Lens platform.
All agents must inherit from BaseAgent and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timezone


class AgentStatus(Enum):
    """Agent execution status"""

    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"


class AgentPriority(Enum):
    """Agent execution priority"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentConfig:
    """Configuration for agent execution"""

    agent_id: str
    priority: AgentPriority = AgentPriority.MEDIUM
    timeout_ms: int = 5000
    max_retries: int = 3
    enable_cache: bool = True
    cache_ttl_seconds: int = 300
    log_level: str = "INFO"

    def __post_init__(self):
        """Validate configuration"""
        if self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")


@dataclass
class AgentResult:
    """Result from agent execution"""

    agent_id: str
    status: AgentStatus
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        """Validate result"""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "score": self.score,
            "confidence": self.confidence,
            "data": self.data,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResult":
        """Create AgentResult from dictionary"""
        return cls(
            agent_id=data["agent_id"],
            status=AgentStatus(data["status"]),
            score=data["score"],
            confidence=data["confidence"],
            data=data["data"],
            metadata=data["metadata"],
            error_message=data.get("error_message"),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            timestamp=data.get("timestamp", ""),
        )


class BaseAgent(ABC):
    """
    Abstract base class for all Aegis Lens AI agents.

    All agents must inherit from this class and implement:
    - process(): Main processing logic
    - validate_input(): Input validation
    - validate_output(): Output validation
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with configuration.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.logger = self._setup_logger()
        self._execution_count = 0
        self._error_count = 0

    def _setup_logger(self) -> logging.Logger:
        """
        Set up logger for the agent.

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f"aegis.agents.{self.config.agent_id}")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # Add console handler if not already present
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data before processing.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Main processing logic for the agent.

        Args:
            input_data: Input data to process

        Returns:
            AgentResult with processing results
        """
        pass

    @abstractmethod
    def validate_output(self, result: AgentResult) -> bool:
        """
        Validate output result.

        Args:
            result: Result to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent with input validation and error handling.

        Args:
            input_data: Input data to process

        Returns:
            AgentResult with execution results
        """
        import time

        start_time = time.time()

        self._execution_count += 1
        self.logger.info(
            f"Executing agent {self.config.agent_id} (execution #{self._execution_count})"
        )

        try:
            # Validate input
            if not self.validate_input(input_data):
                self._error_count += 1
                self.logger.error(f"Input validation failed for agent {self.config.agent_id}")
                return AgentResult(
                    agent_id=self.config.agent_id,
                    status=AgentStatus.ERROR,
                    score=0.0,
                    confidence=0.0,
                    data={},
                    metadata={"validation_error": True},
                    error_message="Input validation failed",
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            # Process data
            result = self.process(input_data)

            # Validate output
            if not self.validate_output(result):
                self.logger.error(f"Output validation failed for agent {self.config.agent_id}")
                result.status = AgentStatus.ERROR
                result.error_message = "Output validation failed"

            result.execution_time_ms = (time.time() - start_time) * 1000
            self.logger.info(
                f"Agent {self.config.agent_id} completed in {result.execution_time_ms:.2f}ms "
                f"with status {result.status.value}"
            )

            return result

        except Exception as e:
            self._error_count += 1
            self.logger.error(
                f"Agent {self.config.agent_id} execution failed: {str(e)}", exc_info=True
            )

            return AgentResult(
                agent_id=self.config.agent_id,
                status=AgentStatus.ERROR,
                score=0.0,
                confidence=0.0,
                data={},
                metadata={"error_type": type(e).__name__},
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent execution statistics.

        Returns:
            Dictionary with execution statistics
        """
        return {
            "agent_id": self.config.agent_id,
            "execution_count": self._execution_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._execution_count, 1),
        }

    def reset_stats(self) -> None:
        """Reset execution statistics."""
        self._execution_count = 0
        self._error_count = 0
        self.logger.info(f"Stats reset for agent {self.config.agent_id}")
