"""
Unit tests for BaseAgent and related classes
"""

import pytest
from typing import Dict, Any
from src.base import (
    BaseAgent,
    AgentConfig,
    AgentResult,
    AgentStatus,
    AgentPriority,
)


class MockAgent(BaseAgent):
    """Mock implementation of BaseAgent for testing"""
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Mock input validation"""
        return "test_key" in input_data
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Mock processing"""
        return AgentResult(
            agent_id=self.config.agent_id,
            status=AgentStatus.COMPLETED,
            score=0.85,
            confidence=0.9,
            data={"processed": True},
            metadata={"input": input_data},
        )
    
    def validate_output(self, result: AgentResult) -> bool:
        """Mock output validation"""
        return result.score >= 0.0 and result.score <= 1.0


class TestAgentConfig:
    """Tests for AgentConfig"""
    
    def test_default_config(self):
        """Test creating config with defaults"""
        config = AgentConfig(agent_id="test_agent")
        assert config.agent_id == "test_agent"
        assert config.priority == AgentPriority.MEDIUM
        assert config.timeout_ms == 5000
        assert config.max_retries == 3
        assert config.enable_cache is True
        assert config.cache_ttl_seconds == 300
        assert config.log_level == "INFO"
    
    def test_custom_config(self):
        """Test creating config with custom values"""
        config = AgentConfig(
            agent_id="test_agent",
            priority=AgentPriority.HIGH,
            timeout_ms=10000,
            max_retries=5,
            enable_cache=False,
            cache_ttl_seconds=600,
            log_level="DEBUG",
        )
        assert config.priority == AgentPriority.HIGH
        assert config.timeout_ms == 10000
        assert config.max_retries == 5
        assert config.enable_cache is False
        assert config.cache_ttl_seconds == 600
        assert config.log_level == "DEBUG"
    
    def test_invalid_timeout(self):
        """Test that invalid timeout raises ValueError"""
        with pytest.raises(ValueError, match="timeout_ms must be positive"):
            AgentConfig(agent_id="test_agent", timeout_ms=0)
        
        with pytest.raises(ValueError, match="timeout_ms must be positive"):
            AgentConfig(agent_id="test_agent", timeout_ms=-100)
    
    def test_invalid_max_retries(self):
        """Test that invalid max_retries raises ValueError"""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            AgentConfig(agent_id="test_agent", max_retries=-1)
    
    def test_invalid_cache_ttl(self):
        """Test that invalid cache_ttl raises ValueError"""
        with pytest.raises(ValueError, match="cache_ttl_seconds must be non-negative"):
            AgentConfig(agent_id="test_agent", cache_ttl_seconds=-1)


class TestAgentResult:
    """Tests for AgentResult"""
    
    def test_valid_result(self):
        """Test creating a valid result"""
        result = AgentResult(
            agent_id="test_agent",
            status=AgentStatus.COMPLETED,
            score=0.85,
            confidence=0.9,
            data={"key": "value"},
            metadata={"meta": "data"},
        )
        assert result.agent_id == "test_agent"
        assert result.status == AgentStatus.COMPLETED
        assert result.score == 0.85
        assert result.confidence == 0.9
        assert result.data == {"key": "value"}
        assert result.metadata == {"meta": "data"}
        assert result.error_message is None
        assert result.execution_time_ms == 0.0
        assert result.timestamp != ""  # Should be auto-generated
    
    def test_invalid_score(self):
        """Test that invalid score raises ValueError"""
        with pytest.raises(ValueError, match="score must be between 0.0 and 1.0"):
            AgentResult(
                agent_id="test_agent",
                status=AgentStatus.COMPLETED,
                score=1.5,
                confidence=0.9,
                data={},
                metadata={},
            )
        
        with pytest.raises(ValueError, match="score must be between 0.0 and 1.0"):
            AgentResult(
                agent_id="test_agent",
                status=AgentStatus.COMPLETED,
                score=-0.1,
                confidence=0.9,
                data={},
                metadata={},
            )
    
    def test_invalid_confidence(self):
        """Test that invalid confidence raises ValueError"""
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            AgentResult(
                agent_id="test_agent",
                status=AgentStatus.COMPLETED,
                score=0.85,
                confidence=1.5,
                data={},
                metadata={},
            )
        
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            AgentResult(
                agent_id="test_agent",
                status=AgentStatus.COMPLETED,
                score=0.85,
                confidence=-0.1,
                data={},
                metadata={},
            )
    
    def test_to_dict(self):
        """Test converting result to dictionary"""
        result = AgentResult(
            agent_id="test_agent",
            status=AgentStatus.COMPLETED,
            score=0.85,
            confidence=0.9,
            data={"key": "value"},
            metadata={"meta": "data"},
            error_message="test error",
            execution_time_ms=100.5,
        )
        result_dict = result.to_dict()
        
        assert result_dict["agent_id"] == "test_agent"
        assert result_dict["status"] == "completed"
        assert result_dict["score"] == 0.85
        assert result_dict["confidence"] == 0.9
        assert result_dict["data"] == {"key": "value"}
        assert result_dict["metadata"] == {"meta": "data"}
        assert result_dict["error_message"] == "test error"
        assert result_dict["execution_time_ms"] == 100.5
    
    def test_from_dict(self):
        """Test creating result from dictionary"""
        data = {
            "agent_id": "test_agent",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "data": {"key": "value"},
            "metadata": {"meta": "data"},
            "error_message": "test error",
            "execution_time_ms": 100.5,
            "timestamp": "2024-01-01T00:00:00",
        }
        result = AgentResult.from_dict(data)
        
        assert result.agent_id == "test_agent"
        assert result.status == AgentStatus.COMPLETED
        assert result.score == 0.85
        assert result.confidence == 0.9
        assert result.data == {"key": "value"}
        assert result.metadata == {"meta": "data"}
        assert result.error_message == "test error"
        assert result.execution_time_ms == 100.5
        assert result.timestamp == "2024-01-01T00:00:00"
    
    def test_from_dict_optional_fields(self):
        """Test creating result from dictionary with optional fields missing"""
        data = {
            "agent_id": "test_agent",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "data": {},
            "metadata": {},
        }
        result = AgentResult.from_dict(data)
        
        assert result.error_message is None
        assert result.execution_time_ms == 0.0
        assert result.timestamp != ""  # Should be auto-generated


class TestBaseAgent:
    """Tests for BaseAgent"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        config = AgentConfig(agent_id="test_agent")
        agent = MockAgent(config)
        
        assert agent.config.agent_id == "test_agent"
        assert agent._execution_count == 0
        assert agent._error_count == 0
    
    def test_execute_success(self):
        """Test successful execution"""
        config = AgentConfig(agent_id="test_agent")
        agent = MockAgent(config)
        
        input_data = {"test_key": "test_value"}
        result = agent.execute(input_data)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.score == 0.85
        assert result.confidence == 0.9
        assert result.data["processed"] is True
        assert result.execution_time_ms > 0
        assert agent._execution_count == 1
        assert agent._error_count == 0
    
    def test_execute_input_validation_failure(self):
        """Test execution with invalid input"""
        config = AgentConfig(agent_id="test_agent")
        agent = MockAgent(config)
        
        input_data = {"invalid_key": "value"}
        result = agent.execute(input_data)
        
        assert result.status == AgentStatus.ERROR
        assert result.score == 0.0
        assert result.confidence == 0.0
        assert result.error_message == "Input validation failed"
        assert result.metadata["validation_error"] is True
        assert agent._execution_count == 1
        assert agent._error_count == 1
    
    def test_execute_output_validation_failure(self):
        """Test execution with output validation failure"""
        
        class FailingOutputAgent(MockAgent):
            def validate_output(self, result: AgentResult) -> bool:
                return False  # Always fail output validation
        
        config = AgentConfig(agent_id="test_agent")
        agent = FailingOutputAgent(config)
        
        input_data = {"test_key": "test_value"}
        result = agent.execute(input_data)
        
        assert result.status == AgentStatus.ERROR
        assert result.error_message == "Output validation failed"
    
    def test_execute_exception_handling(self):
        """Test execution with exception in process"""
        
        class FailingAgent(MockAgent):
            def process(self, input_data: Dict[str, Any]) -> AgentResult:
                raise ValueError("Test exception")
        
        config = AgentConfig(agent_id="test_agent")
        agent = FailingAgent(config)
        
        input_data = {"test_key": "test_value"}
        result = agent.execute(input_data)
        
        assert result.status == AgentStatus.ERROR
        assert result.score == 0.0
        assert result.confidence == 0.0
        assert "Test exception" in result.error_message
        assert result.metadata["error_type"] == "ValueError"
        assert agent._execution_count == 1
        assert agent._error_count == 1
    
    def test_get_stats(self):
        """Test getting execution statistics"""
        config = AgentConfig(agent_id="test_agent")
        agent = MockAgent(config)
        
        # Execute successfully
        agent.execute({"test_key": "value"})
        
        # Execute with failure
        agent.execute({"invalid_key": "value"})
        
        stats = agent.get_stats()
        
        assert stats["agent_id"] == "test_agent"
        assert stats["execution_count"] == 2
        assert stats["error_count"] == 1
        assert stats["error_rate"] == 0.5
    
    def test_reset_stats(self):
        """Test resetting execution statistics"""
        config = AgentConfig(agent_id="test_agent")
        agent = MockAgent(config)
        
        agent.execute({"test_key": "value"})
        agent.execute({"invalid_key": "value"})
        
        assert agent._execution_count == 2
        assert agent._error_count == 1
        
        agent.reset_stats()
        
        assert agent._execution_count == 0
        assert agent._error_count == 0
    
    def test_logger_setup(self):
        """Test logger is properly configured"""
        config = AgentConfig(agent_id="test_agent", log_level="DEBUG")
        agent = MockAgent(config)
        
        assert agent.logger is not None
        assert agent.logger.name == "aegis.agents.test_agent"
        assert agent.logger.level == 10  # DEBUG level


class TestAgentStatus:
    """Tests for AgentStatus enum"""
    
    def test_status_values(self):
        """Test status enum values"""
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.PROCESSING.value == "processing"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.TIMEOUT.value == "timeout"


class TestAgentPriority:
    """Tests for AgentPriority enum"""
    
    def test_priority_values(self):
        """Test priority enum values"""
        assert AgentPriority.LOW.value == "low"
        assert AgentPriority.MEDIUM.value == "medium"
        assert AgentPriority.HIGH.value == "high"
        assert AgentPriority.CRITICAL.value == "critical"
