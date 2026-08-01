"""
Unit tests for Agent Orchestrator
"""

import pytest
from unittest.mock import Mock, patch
from src.orchestrator import (
    AgentOrchestrator,
    OrchestratorConfig,
    OrchestratorResult,
    OrchestratorStrategy,
)
from src.base import BaseAgent, AgentConfig, AgentResult, AgentStatus


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig dataclass"""

    def test_default_config(self):
        """Test creating orchestrator config with defaults"""
        config = OrchestratorConfig(orchestrator_id="test_orchestrator")
        assert config.orchestrator_id == "test_orchestrator"
        assert config.strategy == OrchestratorStrategy.SEQUENTIAL
        assert config.timeout_ms == 30000
        assert config.max_retries == 3
        assert config.enable_caching is True
        assert config.cache_ttl_seconds == 300
        assert config.log_level == "INFO"
        assert config.required_agents == []
        assert config.optional_agents == []
        assert config.aggregation_method == "weighted_average"

    def test_custom_config(self):
        """Test creating orchestrator config with custom values"""
        config = OrchestratorConfig(
            orchestrator_id="custom_orchestrator",
            strategy=OrchestratorStrategy.PARALLEL,
            timeout_ms=60000,
            max_retries=5,
            enable_caching=False,
            cache_ttl_seconds=600,
            log_level="DEBUG",
            required_agents=["agent1", "agent2"],
            optional_agents=["agent3"],
            aggregation_method="majority_vote",
        )
        assert config.orchestrator_id == "custom_orchestrator"
        assert config.strategy == OrchestratorStrategy.PARALLEL
        assert config.timeout_ms == 60000
        assert config.max_retries == 5
        assert config.enable_caching is False
        assert config.cache_ttl_seconds == 600
        assert config.log_level == "DEBUG"
        assert config.required_agents == ["agent1", "agent2"]
        assert config.optional_agents == ["agent3"]
        assert config.aggregation_method == "majority_vote"


class TestAgentOrchestratorInitialization:
    """Tests for AgentOrchestrator initialization"""

    def test_initialization(self):
        """Test orchestrator initialization"""
        config = OrchestratorConfig(orchestrator_id="test_orch")
        orchestrator = AgentOrchestrator(config)
        assert orchestrator.config == config
        assert orchestrator.agents == {}

    def test_initialization_with_strategy(self):
        """Test orchestrator with different strategies"""
        for strategy in OrchestratorStrategy:
            config = OrchestratorConfig(
                orchestrator_id="test_orch",
                strategy=strategy,
            )
            orchestrator = AgentOrchestrator(config)
            assert orchestrator.config.strategy == strategy


class TestAgentRegistration:
    """Tests for agent registration"""

    def test_register_agent(self):
        """Test registering an agent"""
        config = OrchestratorConfig(orchestrator_id="test_orch")
        orchestrator = AgentOrchestrator(config)

        mock_agent = Mock(spec=BaseAgent)
        mock_agent.config = Mock(spec=AgentConfig)
        mock_agent.config.agent_id = "agent1"

        orchestrator.register_agent(mock_agent)
        assert "agent1" in orchestrator.agents
        assert orchestrator.agents["agent1"] == mock_agent

    def test_unregister_agent(self):
        """Test unregistering an agent"""
        config = OrchestratorConfig(orchestrator_id="test_orch")
        orchestrator = AgentOrchestrator(config)

        mock_agent = Mock(spec=BaseAgent)
        mock_agent.config = Mock(spec=AgentConfig)
        mock_agent.config.agent_id = "agent1"

        orchestrator.register_agent(mock_agent)
        assert "agent1" in orchestrator.agents

        orchestrator.unregister_agent("agent1")
        assert "agent1" not in orchestrator.agents

    def test_unregister_nonexistent_agent(self):
        """Test unregistering a non-existent agent"""
        config = OrchestratorConfig(orchestrator_id="test_orch")
        orchestrator = AgentOrchestrator(config)

        # Should not raise an error
        orchestrator.unregister_agent("nonexistent")


class TestAgentValidation:
    """Tests for agent validation"""

    def test_validate_agents_success(self):
        """Test validation when all required agents are registered"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        assert orchestrator.validate_agents() is True

    def test_validate_agents_missing_required(self):
        """Test validation when required agents are missing"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"

        orchestrator.register_agent(mock_agent1)

        assert orchestrator.validate_agents() is False


class TestSequentialExecution:
    """Tests for sequential execution strategy"""

    def test_execute_sequential_success(self):
        """Test sequential execution with successful agents"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            strategy=OrchestratorStrategy.SEQUENTIAL,
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.status == AgentStatus.COMPLETED
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.overall_confidence <= 1.0
        assert len(result.agent_results) == 2

    def test_execute_sequential_with_failure(self):
        """Test sequential execution when one agent fails"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            strategy=OrchestratorStrategy.SEQUENTIAL,
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(side_effect=Exception("Agent failed"))

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        # Should still execute agent2 even if agent1 fails
        assert len(result.agent_results) == 1
        assert "agent2" in result.agent_results


class TestParallelExecution:
    """Tests for parallel execution strategy"""

    def test_execute_parallel_success(self):
        """Test parallel execution with successful agents"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            strategy=OrchestratorStrategy.PARALLEL,
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.status == AgentStatus.COMPLETED
        assert len(result.agent_results) == 2


class TestPriorityBasedExecution:
    """Tests for priority-based execution strategy"""

    def test_execute_priority_based(self):
        """Test priority-based execution"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            strategy=OrchestratorStrategy.PRIORITY_BASED,
            required_agents=["agent1", "agent2", "agent3"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.config.priority = "high"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.config.priority = "medium"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        mock_agent3 = Mock(spec=BaseAgent)
        mock_agent3.config = Mock(spec=AgentConfig)
        mock_agent3.config.agent_id = "agent3"
        mock_agent3.config.priority = "low"
        mock_agent3.execute = Mock(
            return_value=AgentResult(
                agent_id="agent3",
                status=AgentStatus.COMPLETED,
                score=0.6,
                confidence=0.8,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)
        orchestrator.register_agent(mock_agent3)

        result = orchestrator.execute({"test": "data"})

        assert result.status == AgentStatus.COMPLETED
        assert len(result.agent_results) == 3


class TestResultAggregation:
    """Tests for result aggregation methods"""

    def test_aggregate_weighted_average(self):
        """Test weighted average aggregation"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            aggregation_method="weighted_average",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.6,
                confidence=0.5,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        # Weighted average: (0.8*0.9 + 0.6*0.5) / (0.9 + 0.5) = (0.72 + 0.3) / 1.4 = 0.728
        assert abs(result.overall_score - 0.728) < 0.01

    def test_aggregate_majority_vote(self):
        """Test majority vote aggregation"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            aggregation_method="majority_vote",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.aggregated_data["method"] == "majority_vote"

    def test_aggregate_min(self):
        """Test min aggregation"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            aggregation_method="min",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.6,
                confidence=0.5,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.overall_score == 0.6
        assert result.overall_confidence == 0.5

    def test_aggregate_max(self):
        """Test max aggregation"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            aggregation_method="max",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.6,
                confidence=0.5,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.overall_score == 0.8
        assert result.overall_confidence == 0.9


class TestOverallStatusDetermination:
    """Tests for overall status determination"""

    def test_determine_status_all_completed(self):
        """Test status when all agents complete"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            required_agents=["agent1", "agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.status == AgentStatus.COMPLETED

    def test_determine_status_required_fails(self):
        """Test status when required agent fails"""
        config = OrchestratorConfig(
            orchestrator_id="test_orch",
            required_agents=["agent1"],
            optional_agents=["agent2"],
        )
        orchestrator = AgentOrchestrator(config)

        mock_agent1 = Mock(spec=BaseAgent)
        mock_agent1.config = Mock(spec=AgentConfig)
        mock_agent1.config.agent_id = "agent1"
        mock_agent1.execute = Mock(
            return_value=AgentResult(
                agent_id="agent1",
                status=AgentStatus.ERROR,
                score=0.0,
                confidence=0.0,
                data={},
                metadata={},
            )
        )

        mock_agent2 = Mock(spec=BaseAgent)
        mock_agent2.config = Mock(spec=AgentConfig)
        mock_agent2.config.agent_id = "agent2"
        mock_agent2.execute = Mock(
            return_value=AgentResult(
                agent_id="agent2",
                status=AgentStatus.COMPLETED,
                score=0.7,
                confidence=0.85,
                data={},
                metadata={},
            )
        )

        orchestrator.register_agent(mock_agent1)
        orchestrator.register_agent(mock_agent2)

        result = orchestrator.execute({"test": "data"})

        assert result.status == AgentStatus.ERROR


class TestOrchestratorResult:
    """Tests for OrchestratorResult dataclass"""

    def test_orchestrator_result_creation(self):
        """Test creating orchestrator result"""
        result = OrchestratorResult(
            orchestrator_id="test_orch",
            status=AgentStatus.COMPLETED,
            overall_score=0.8,
            overall_confidence=0.9,
        )
        assert result.orchestrator_id == "test_orch"
        assert result.status == AgentStatus.COMPLETED
        assert result.overall_score == 0.8
        assert result.overall_confidence == 0.9
        assert result.agent_results == {}
        assert result.aggregated_data == {}
        assert result.metadata == {}
        assert result.error_message is None

    def test_orchestrator_result_with_error(self):
        """Test creating orchestrator result with error"""
        result = OrchestratorResult(
            orchestrator_id="test_orch",
            status=AgentStatus.ERROR,
            overall_score=0.0,
            overall_confidence=0.0,
            error_message="Execution failed",
        )
        assert result.status == AgentStatus.ERROR
        assert result.error_message == "Execution failed"
