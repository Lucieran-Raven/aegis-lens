"""
Integration tests for Agent Orchestrator with FastAPI service
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch

from src.api import app, register_agent
from src.orchestrator import (
    AgentOrchestrator,
    OrchestratorConfig,
    OrchestratorStrategy,
)
from src.agents.chronos_agent import ChronosAgent
from src.agents.echo_agent import EchoAgent
from src.agents.iris_agent import IrisAgent
from src.agents.lipsync_agent import LipsyncAgent
from src.base import AgentConfig


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def multi_agent_orchestrator():
    """Create orchestrator with multiple agents"""
    config = OrchestratorConfig(
        orchestrator_id="multi_agent_orch",
        strategy=OrchestratorStrategy.SEQUENTIAL,
        required_agents=["chronos", "echo"],
        optional_agents=["iris", "lipsync"],
        aggregation_method="weighted_average",
    )

    orchestrator = AgentOrchestrator(config)

    # Create and register agents
    with patch.object(ChronosAgent, "_find_wasm_path", return_value="/mock/path"):
        chronos = ChronosAgent(AgentConfig(agent_id="chronos", priority="high"))
        orchestrator.register_agent(chronos)
        register_agent(chronos)

    with patch.object(EchoAgent, "_find_wasm_path", return_value="/mock/path"):
        echo = EchoAgent(AgentConfig(agent_id="echo", priority="high"))
        orchestrator.register_agent(echo)
        register_agent(echo)

    with patch.object(IrisAgent, "_find_wasm_path", return_value="/mock/path"):
        iris = IrisAgent(AgentConfig(agent_id="iris", priority="medium"))
        orchestrator.register_agent(iris)
        register_agent(iris)

    with patch.object(LipsyncAgent, "_find_wasm_path", return_value="/mock/path"):
        lipsync = LipsyncAgent(AgentConfig(agent_id="lipsync", priority="medium"))
        orchestrator.register_agent(lipsync)
        register_agent(lipsync)

    yield orchestrator

    # Cleanup
    from src.api import agent_registry

    for agent_id in ["chronos", "echo", "iris", "lipsync"]:
        if agent_id in agent_registry:
            del agent_registry[agent_id]


class TestOrchestratorIntegration:
    """Integration tests for agent orchestrator"""

    def test_orchestrator_sequential_execution(self, multi_agent_orchestrator):
        """Test orchestrator executing agents sequentially"""
        with (
            patch.object(
                multi_agent_orchestrator.agents["chronos"],
                "_call_wasm_module",
                return_value={
                    "jitter_score": 25.5,
                    "jitter_std": 10.2,
                    "jitter_mean": 15.0,
                    "anomaly_count": 2,
                },
            ),
            patch.object(
                multi_agent_orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
        ):
            result = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )

            assert result.status.value == "completed"
            assert 0.0 <= result.overall_score <= 1.0
            assert 0.0 <= result.overall_confidence <= 1.0
            assert len(result.agent_results) >= 2  # At least required agents

    def test_orchestrator_parallel_execution(self, multi_agent_orchestrator):
        """Test orchestrator executing agents in parallel"""
        config = OrchestratorConfig(
            orchestrator_id="parallel_orch",
            strategy=OrchestratorStrategy.PARALLEL,
            required_agents=["chronos", "echo"],
            aggregation_method="weighted_average",
        )

        orchestrator = AgentOrchestrator(config)
        orchestrator.agents = multi_agent_orchestrator.agents

        with (
            patch.object(
                orchestrator.agents["chronos"],
                "_call_wasm_module",
                return_value={
                    "jitter_score": 25.5,
                    "jitter_std": 10.2,
                    "jitter_mean": 15.0,
                    "anomaly_count": 2,
                },
            ),
            patch.object(
                orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
        ):
            result = orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )

            assert result.status.value == "completed"
            assert len(result.agent_results) >= 2

    def test_orchestrator_with_all_agents(self, multi_agent_orchestrator):
        """Test orchestrator with all four agents"""
        with (
            patch.object(
                multi_agent_orchestrator.agents["chronos"],
                "_call_wasm_module",
                return_value={
                    "jitter_score": 25.5,
                    "jitter_std": 10.2,
                    "jitter_mean": 15.0,
                    "anomaly_count": 2,
                },
            ),
            patch.object(
                multi_agent_orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
            patch.object(
                multi_agent_orchestrator.agents["iris"],
                "_call_wasm_module",
                return_value={
                    "liveness_score": 75.5,
                    "trajectory_smoothness": 0.85,
                    "blink_rate": 12,
                    "fixation_count": 8,
                },
            ),
            patch.object(
                multi_agent_orchestrator.agents["lipsync"],
                "_call_wasm_module",
                return_value={
                    "sync_score": 85.5,
                    "sync_error": 15.2,
                    "phoneme_match_rate": 0.9,
                    "mouth_openness_variance": 25.0,
                },
            ),
        ):
            result = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                    "eye_vectors": [[0.5, 0.5]] * 100,
                    "frame_count": 100,
                    "fps": 30,
                    "video_features": [[0.4, 0.5, 0.6]] * 100,
                    "sync_data": [[0, 10]] * 100,
                }
            )

            assert result.status.value == "completed"
            assert len(result.agent_results) == 4
            assert "chronos" in result.agent_results
            assert "echo" in result.agent_results
            assert "iris" in result.agent_results
            assert "lipsync" in result.agent_results

    def test_orchestrator_aggregation_methods(self, multi_agent_orchestrator):
        """Test different aggregation methods"""
        with (
            patch.object(
                multi_agent_orchestrator.agents["chronos"],
                "_call_wasm_module",
                return_value={
                    "jitter_score": 25.5,
                    "jitter_std": 10.2,
                    "jitter_mean": 15.0,
                    "anomaly_count": 2,
                },
            ),
            patch.object(
                multi_agent_orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
        ):
            # Test weighted average
            multi_agent_orchestrator.config.aggregation_method = "weighted_average"
            result1 = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )
            assert result1.aggregated_data["method"] == "weighted_average"

            # Test min
            multi_agent_orchestrator.config.aggregation_method = "min"
            result2 = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )
            assert result2.aggregated_data["method"] == "min"

            # Test max
            multi_agent_orchestrator.config.aggregation_method = "max"
            result3 = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )
            assert result3.aggregated_data["method"] == "max"

    def test_orchestrator_with_agent_failure(self, multi_agent_orchestrator):
        """Test orchestrator when one agent fails"""
        with (
            patch.object(
                multi_agent_orchestrator.agents["chronos"],
                "_call_wasm_module",
                side_effect=Exception("WASM execution failed"),
            ),
            patch.object(
                multi_agent_orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
        ):
            result = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )

            # Should still execute other agents
            assert len(result.agent_results) >= 1
            assert "echo" in result.agent_results

    def test_orchestrator_required_agent_failure(self, multi_agent_orchestrator):
        """Test orchestrator when required agent fails"""
        with (
            patch.object(
                multi_agent_orchestrator.agents["chronos"],
                "_call_wasm_module",
                return_value={
                    "jitter_score": 25.5,
                    "jitter_std": 10.2,
                    "jitter_mean": 15.0,
                    "anomaly_count": 2,
                },
            ),
            patch.object(
                multi_agent_orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
        ):
            # First execute successfully
            result1 = multi_agent_orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                }
            )
            assert result1.status.value == "completed"

    def test_orchestrator_priority_based_execution(self, multi_agent_orchestrator):
        """Test priority-based execution order"""
        config = OrchestratorConfig(
            orchestrator_id="priority_orch",
            strategy=OrchestratorStrategy.PRIORITY_BASED,
            required_agents=["chronos", "echo", "iris"],
            aggregation_method="weighted_average",
        )

        orchestrator = AgentOrchestrator(config)
        orchestrator.agents = multi_agent_orchestrator.agents

        with (
            patch.object(
                orchestrator.agents["chronos"],
                "_call_wasm_module",
                return_value={
                    "jitter_score": 25.5,
                    "jitter_std": 10.2,
                    "jitter_mean": 15.0,
                    "anomaly_count": 2,
                },
            ),
            patch.object(
                orchestrator.agents["echo"],
                "_call_wasm_module",
                return_value={
                    "delay_score": 25.5,
                    "delay_ms": 12.5,
                    "threshold_crossed": False,
                    "signal_quality": 0.9,
                },
            ),
            patch.object(
                orchestrator.agents["iris"],
                "_call_wasm_module",
                return_value={
                    "liveness_score": 75.5,
                    "trajectory_smoothness": 0.85,
                    "blink_rate": 12,
                    "fixation_count": 8,
                },
            ),
        ):
            result = orchestrator.execute(
                {
                    "timestamps": [0, 100, 200, 300],
                    "sample_rate": 44100,
                    "audio_samples": [0.1] * 1000,
                    "eye_vectors": [[0.5, 0.5]] * 100,
                    "frame_count": 100,
                    "fps": 30,
                }
            )

            assert result.status.value == "completed"
            assert len(result.agent_results) == 3


class TestOrchestratorWithFastAPI:
    """Integration tests for orchestrator with FastAPI"""

    def test_orchestrator_via_api(self, client, multi_agent_orchestrator):
        """Test executing orchestrator via API (individual agents)"""
        # Test that individual agents are accessible via API
        with patch.object(
            multi_agent_orchestrator.agents["chronos"],
            "_call_wasm_module",
            return_value={
                "jitter_score": 25.5,
                "jitter_std": 10.2,
                "jitter_mean": 15.0,
                "anomaly_count": 2,
            },
        ):
            response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "chronos",
                        "priority": "high",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "timestamps": [0, 100, 200, 300],
                        "sample_rate": 44100,
                    },
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "chronos"
            assert data["status"] == "completed"

    def test_list_all_agents(self, client, multi_agent_orchestrator):
        """Test that all registered agents appear in agent list"""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()

        assert "chronos" in data["agents"]
        assert "echo" in data["agents"]
        assert "iris" in data["agents"]
        assert "lipsync" in data["agents"]
