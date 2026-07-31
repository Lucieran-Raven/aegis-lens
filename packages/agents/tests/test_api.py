"""
Unit tests for FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api import app, register_agent, unregister_agent, agent_registry
from src.base import BaseAgent, AgentConfig, AgentResult, AgentStatus, AgentPriority


class MockAgent(BaseAgent):
    """Mock agent for testing"""
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "test_key" in input_data
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent_id=self.config.agent_id,
            status=AgentStatus.COMPLETED,
            score=0.85,
            confidence=0.9,
            data={"processed": True},
            metadata={"input": input_data},
        )
    
    def validate_output(self, result: AgentResult) -> bool:
        return result.score >= 0.0 and result.score <= 1.0


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Create mock agent for testing"""
    config = AgentConfig(agent_id="test_agent")
    agent = MockAgent(config)
    register_agent(agent)
    yield agent
    unregister_agent("test_agent")


class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "aegis-agents"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data


class TestAgentExecution:
    """Tests for agent execution endpoint"""
    
    def test_execute_agent_success(self, client, mock_agent):
        """Test successful agent execution"""
        request = {
            "config": {
                "agent_id": "test_agent",
                "priority": "medium",
                "timeout_ms": 5000,
                "max_retries": 3,
                "enable_cache": True,
                "cache_ttl_seconds": 300,
                "log_level": "INFO",
            },
            "input_data": {"test_key": "test_value"},
        }
        response = client.post("/execute", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert data["status"] == "completed"
        assert data["score"] == 0.85
        assert data["confidence"] == 0.9
        assert data["data"]["processed"] is True
        assert data["execution_time_ms"] >= 0
        assert "timestamp" in data
    
    def test_execute_agent_not_found(self, client):
        """Test execution with non-existent agent"""
        request = {
            "config": {
                "agent_id": "non_existent_agent",
                "priority": "medium",
            },
            "input_data": {"test_key": "test_value"},
        }
        response = client.post("/execute", json=request)
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_execute_agent_invalid_input(self, client, mock_agent):
        """Test execution with invalid input"""
        request = {
            "config": {
                "agent_id": "test_agent",
                "priority": "medium",
            },
            "input_data": {"invalid_key": "value"},
        }
        response = client.post("/execute", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["score"] == 0.0
        assert data["confidence"] == 0.0
        assert "validation" in data["error_message"].lower()
    
    def test_execute_agent_invalid_config(self, client):
        """Test execution with invalid configuration"""
        request = {
            "config": {
                "agent_id": "test_agent",
                "priority": "medium",
                "timeout_ms": -1,  # Invalid
            },
            "input_data": {"test_key": "test_value"},
        }
        response = client.post("/execute", json=request)
        assert response.status_code == 400
        data = response.json()
        assert "invalid configuration" in data["detail"].lower()
    
    def test_execute_agent_priority_variations(self, client, mock_agent):
        """Test execution with different priority levels"""
        priorities = ["low", "medium", "high", "critical"]
        for priority in priorities:
            request = {
                "config": {
                    "agent_id": "test_agent",
                    "priority": priority,
                },
                "input_data": {"test_key": "test_value"},
            }
            response = client.post("/execute", json=request)
            assert response.status_code == 200


class TestListAgents:
    """Tests for list agents endpoint"""
    
    def test_list_agents_empty(self, client):
        """Test listing agents when none registered"""
        # Clear registry
        agent_registry.clear()
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["agents"] == []
        assert data["count"] == 0
    
    def test_list_agents_with_registered(self, client, mock_agent):
        """Test listing agents with registered agent"""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "test_agent" in data["agents"]
        assert data["count"] >= 1


class TestAgentStats:
    """Tests for agent statistics endpoint"""
    
    def test_get_agent_stats(self, client, mock_agent):
        """Test getting agent statistics"""
        # Execute agent to generate stats
        mock_agent.execute({"test_key": "value"})
        
        response = client.get("/agents/test_agent/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert data["execution_count"] >= 1
        assert data["error_count"] >= 0
        assert 0.0 <= data["error_rate"] <= 1.0
    
    def test_get_agent_stats_not_found(self, client):
        """Test getting stats for non-existent agent"""
        response = client.get("/agents/non_existent/stats")
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"].lower()


class TestResetAgentStats:
    """Tests for reset agent stats endpoint"""
    
    def test_reset_agent_stats(self, client, mock_agent):
        """Test resetting agent statistics"""
        # Execute agent to generate stats
        mock_agent.execute({"test_key": "value"})
        mock_agent.execute({"test_key": "value"})
        
        # Reset stats
        response = client.post("/agents/test_agent/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert "reset" in data["message"].lower()
        
        # Verify stats are reset
        stats = mock_agent.get_stats()
        assert stats["execution_count"] == 0
        assert stats["error_count"] == 0
    
    def test_reset_agent_stats_not_found(self, client):
        """Test resetting stats for non-existent agent"""
        response = client.post("/agents/non_existent/reset")
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"].lower()


class TestAgentRegistration:
    """Tests for agent registration functions"""
    
    def test_register_agent(self):
        """Test registering an agent"""
        config = AgentConfig(agent_id="new_agent")
        agent = MockAgent(config)
        
        register_agent(agent)
        assert "new_agent" in agent_registry
        unregister_agent("new_agent")
    
    def test_unregister_agent(self):
        """Test unregistering an agent"""
        config = AgentConfig(agent_id="temp_agent")
        agent = MockAgent(config)
        register_agent(agent)
        
        unregister_agent("temp_agent")
        assert "temp_agent" not in agent_registry
    
    def test_register_duplicate_agent(self):
        """Test registering duplicate agent (should overwrite)"""
        config1 = AgentConfig(agent_id="dup_agent")
        agent1 = MockAgent(config1)
        register_agent(agent1)
        
        config2 = AgentConfig(agent_id="dup_agent")
        agent2 = MockAgent(config2)
        register_agent(agent2)
        
        assert agent_registry["dup_agent"] == agent2
        unregister_agent("dup_agent")


class TestRequestModels:
    """Tests for Pydantic request models"""
    
    def test_agent_config_request_defaults(self):
        """Test AgentConfigRequest with defaults"""
        from src.api import AgentConfigRequest
        config = AgentConfigRequest(agent_id="test")
        assert config.priority == "medium"
        assert config.timeout_ms == 5000
        assert config.max_retries == 3
        assert config.enable_cache is True
        assert config.cache_ttl_seconds == 300
        assert config.log_level == "INFO"
    
    def test_agent_config_request_custom(self):
        """Test AgentConfigRequest with custom values"""
        from src.api import AgentConfigRequest
        config = AgentConfigRequest(
            agent_id="test",
            priority="high",
            timeout_ms=10000,
            max_retries=5,
            enable_cache=False,
            cache_ttl_seconds=600,
            log_level="DEBUG",
        )
        assert config.priority == "high"
        assert config.timeout_ms == 10000
        assert config.max_retries == 5
        assert config.enable_cache is False
        assert config.cache_ttl_seconds == 600
        assert config.log_level == "DEBUG"
    
    def test_agent_execute_request(self):
        """Test AgentExecuteRequest"""
        from src.api import AgentExecuteRequest, AgentConfigRequest
        request = AgentExecuteRequest(
            config=AgentConfigRequest(agent_id="test"),
            input_data={"key": "value"},
        )
        assert request.config.agent_id == "test"
        assert request.input_data == {"key": "value"}
