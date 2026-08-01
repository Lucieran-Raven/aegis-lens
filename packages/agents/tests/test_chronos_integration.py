"""
Integration tests for CHRONOS Agent with FastAPI service
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch

from src.api import app, register_agent
from src.agents.chronos_agent import ChronosAgent
from src.base import AgentConfig


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def chronos_agent():
    """Create and register CHRONOS agent"""
    config = AgentConfig(
        agent_id="chronos_integration",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )
    with patch.object(ChronosAgent, "_find_wasm_path", return_value="/mock/path"):
        agent = ChronosAgent(config)
        register_agent(agent)
        yield agent
        # Cleanup
        from src.api import agent_registry
        if "chronos_integration" in agent_registry:
            del agent_registry["chronos_integration"]


class TestChronosAgentAPIIntegration:
    """Integration tests for CHRONOS agent with FastAPI"""

    def test_execute_chronos_via_api(self, client, chronos_agent):
        """Test executing CHRONOS agent via API"""
        with patch.object(
            chronos_agent,
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
                        "agent_id": "chronos_integration",
                        "priority": "medium",
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
            assert data["agent_id"] == "chronos_integration"
            assert data["status"] == "completed"
            assert 0.0 <= data["score"] <= 1.0
            assert 0.0 <= data["confidence"] <= 1.0
            assert "jitter_score" in data["data"]
            assert data["data"]["jitter_score"] == 25.5

    def test_execute_chronos_invalid_input(self, client, chronos_agent):
        """Test executing CHRONOS agent with invalid input via API"""
        response = client.post(
            "/execute",
            json={
                "config": {
                    "agent_id": "chronos_integration",
                    "priority": "medium",
                    "timeout_ms": 5000,
                    "max_retries": 3,
                    "enable_cache": False,
                    "cache_ttl_seconds": 300,
                    "log_level": "INFO",
                },
                "input_data": {
                    "timestamps": [0],  # Insufficient timestamps
                    "sample_rate": 44100,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error_message"] == "Input validation failed"

    def test_list_agents_includes_chronos(self, client, chronos_agent):
        """Test that CHRONOS agent appears in agent list"""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "chronos_integration" in data["agents"]

    def test_get_chronos_stats(self, client, chronos_agent):
        """Test getting CHRONOS agent statistics"""
        # Execute agent once to generate stats
        with patch.object(
            chronos_agent,
            "_call_wasm_module",
            return_value={
                "jitter_score": 25.5,
                "jitter_std": 10.2,
                "jitter_mean": 15.0,
                "anomaly_count": 2,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "chronos_integration",
                        "priority": "medium",
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

        # Get stats
        response = client.get("/agents/chronos_integration/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "chronos_integration"
        assert data["execution_count"] >= 1
        assert data["error_rate"] >= 0.0

    def test_reset_chronos_stats(self, client, chronos_agent):
        """Test resetting CHRONOS agent statistics"""
        # Execute agent once
        with patch.object(
            chronos_agent,
            "_call_wasm_module",
            return_value={
                "jitter_score": 25.5,
                "jitter_std": 10.2,
                "jitter_mean": 15.0,
                "anomaly_count": 2,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "chronos_integration",
                        "priority": "medium",
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

        # Reset stats
        response = client.post("/agents/chronos_integration/reset")
        assert response.status_code == 200
        data = response.json()
        assert "Statistics reset" in data["message"]

        # Verify stats are reset
        response = client.get("/agents/chronos_integration/stats")
        data = response.json()
        assert data["execution_count"] == 0
        assert data["error_count"] == 0

    def test_execute_nonexistent_agent(self, client):
        """Test executing non-existent agent"""
        response = client.post(
            "/execute",
            json={
                "config": {
                    "agent_id": "nonexistent_agent",
                    "priority": "medium",
                    "timeout_ms": 5000,
                    "max_retries": 3,
                    "enable_cache": False,
                    "cache_ttl_seconds": 300,
                    "log_level": "INFO",
                },
                "input_data": {
                    "timestamps": [0, 100, 200],
                    "sample_rate": 44100,
                },
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]


class TestChronosAgentEndToEnd:
    """End-to-end tests for CHRONOS agent workflow"""

    def test_full_chronos_workflow(self, client, chronos_agent):
        """Test complete CHRONOS agent workflow"""
        with patch.object(
            chronos_agent,
            "_call_wasm_module",
            return_value={
                "jitter_score": 25.5,
                "jitter_std": 10.2,
                "jitter_mean": 15.0,
                "anomaly_count": 2,
            },
        ):
            # Step 1: Check agent is registered
            list_response = client.get("/agents")
            assert "chronos_integration" in list_response.json()["agents"]

            # Step 2: Execute agent with valid data
            execute_response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "chronos_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "timestamps": [0, 100, 200, 300, 400],
                        "sample_rate": 44100,
                    },
                },
            )
            assert execute_response.status_code == 200
            result = execute_response.json()
            assert result["status"] == "completed"

            # Step 3: Verify stats updated
            stats_response = client.get("/agents/chronos_integration/stats")
            stats = stats_response.json()
            assert stats["execution_count"] == 1

            # Step 4: Execute again with different data
            with patch.object(
                chronos_agent,
                "_call_wasm_module",
                return_value={
                    "jitter_score": 85.0,
                    "jitter_std": 60.0,
                    "jitter_mean": 50.0,
                    "anomaly_count": 15,
                },
            ):
                execute_response2 = client.post(
                    "/execute",
                    json={
                        "config": {
                            "agent_id": "chronos_integration",
                            "priority": "medium",
                            "timeout_ms": 5000,
                            "max_retries": 3,
                            "enable_cache": False,
                            "cache_ttl_seconds": 300,
                            "log_level": "INFO",
                        },
                        "input_data": {
                            "timestamps": [0, 150, 300, 450],
                            "sample_rate": 48000,
                        },
                    },
                )
                assert execute_response2.status_code == 200
                result2 = execute_response2.json()
                assert result2["score"] > 0.7  # High jitter

            # Step 5: Verify stats updated again
            stats_response2 = client.get("/agents/chronos_integration/stats")
            stats2 = stats_response2.json()
            assert stats2["execution_count"] == 2
