"""
Integration tests for IRIS Agent with FastAPI service
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch

from src.api import app, register_agent
from src.agents.iris_agent import IrisAgent
from src.base import AgentConfig


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def iris_agent():
    """Create and register IRIS agent"""
    config = AgentConfig(
        agent_id="iris_integration",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )
    with patch.object(IrisAgent, "_find_wasm_path", return_value="/mock/path"):
        agent = IrisAgent(config)
        register_agent(agent)
        yield agent
        # Cleanup
        from src.api import agent_registry
        if "iris_integration" in agent_registry:
            del agent_registry["iris_integration"]


class TestIrisAgentAPIIntegration:
    """Integration tests for IRIS agent with FastAPI"""

    def test_execute_iris_via_api(self, client, iris_agent):
        """Test executing IRIS agent via API"""
        with patch.object(
            iris_agent,
            "_call_wasm_module",
            return_value={
                "liveness_score": 75.5,
                "trajectory_smoothness": 0.85,
                "blink_rate": 12,
                "fixation_count": 8,
            },
        ):
            response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "iris_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "eye_vectors": [[0.5, 0.5]] * 100,
                        "frame_count": 100,
                        "fps": 30,
                    },
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "iris_integration"
            assert data["status"] == "completed"
            assert 0.0 <= data["score"] <= 1.0
            assert 0.0 <= data["confidence"] <= 1.0
            assert "liveness_score" in data["data"]
            assert data["data"]["liveness_score"] == 75.5

    def test_execute_iris_invalid_input(self, client, iris_agent):
        """Test executing IRIS agent with invalid input via API"""
        response = client.post(
            "/execute",
            json={
                "config": {
                    "agent_id": "iris_integration",
                    "priority": "medium",
                    "timeout_ms": 5000,
                    "max_retries": 3,
                    "enable_cache": False,
                    "cache_ttl_seconds": 300,
                    "log_level": "INFO",
                },
                "input_data": {
                    "eye_vectors": [[0.5, 0.5]] * 5,  # Insufficient vectors
                    "frame_count": 100,
                    "fps": 30,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error_message"] == "Input validation failed"

    def test_list_agents_includes_iris(self, client, iris_agent):
        """Test that IRIS agent appears in agent list"""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "iris_integration" in data["agents"]

    def test_get_iris_stats(self, client, iris_agent):
        """Test getting IRIS agent statistics"""
        # Execute agent once to generate stats
        with patch.object(
            iris_agent,
            "_call_wasm_module",
            return_value={
                "liveness_score": 75.5,
                "trajectory_smoothness": 0.85,
                "blink_rate": 12,
                "fixation_count": 8,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "iris_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "eye_vectors": [[0.5, 0.5]] * 100,
                        "frame_count": 100,
                        "fps": 30,
                    },
                },
            )

        # Get stats
        response = client.get("/agents/iris_integration/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "iris_integration"
        assert data["execution_count"] >= 1
        assert data["error_rate"] >= 0.0

    def test_reset_iris_stats(self, client, iris_agent):
        """Test resetting IRIS agent statistics"""
        # Execute agent once
        with patch.object(
            iris_agent,
            "_call_wasm_module",
            return_value={
                "liveness_score": 75.5,
                "trajectory_smoothness": 0.85,
                "blink_rate": 12,
                "fixation_count": 8,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "iris_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "eye_vectors": [[0.5, 0.5]] * 100,
                        "frame_count": 100,
                        "fps": 30,
                    },
                },
            )

        # Reset stats
        response = client.post("/agents/iris_integration/reset")
        assert response.status_code == 200
        data = response.json()
        assert "Statistics reset" in data["message"]

        # Verify stats are reset
        response = client.get("/agents/iris_integration/stats")
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
                    "eye_vectors": [[0.5, 0.5]] * 100,
                    "frame_count": 100,
                    "fps": 30,
                },
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]


class TestIrisAgentEndToEnd:
    """End-to-end tests for IRIS agent workflow"""

    def test_full_iris_workflow(self, client, iris_agent):
        """Test complete IRIS agent workflow"""
        with patch.object(
            iris_agent,
            "_call_wasm_module",
            return_value={
                "liveness_score": 75.5,
                "trajectory_smoothness": 0.85,
                "blink_rate": 12,
                "fixation_count": 8,
            },
        ):
            # Step 1: Check agent is registered
            list_response = client.get("/agents")
            assert "iris_integration" in list_response.json()["agents"]

            # Step 2: Execute agent with valid data
            execute_response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "iris_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "eye_vectors": [[0.5, 0.5]] * 150,
                        "frame_count": 150,
                        "fps": 30,
                    },
                },
            )
            assert execute_response.status_code == 200
            result = execute_response.json()
            assert result["status"] == "completed"

            # Step 3: Verify stats updated
            stats_response = client.get("/agents/iris_integration/stats")
            stats = stats_response.json()
            assert stats["execution_count"] == 1

            # Step 4: Execute again with different data
            with patch.object(
                iris_agent,
                "_call_wasm_module",
                return_value={
                    "liveness_score": 15.0,
                    "trajectory_smoothness": 0.3,
                    "blink_rate": 2,
                    "fixation_count": 2,
                },
            ):
                execute_response2 = client.post(
                    "/execute",
                    json={
                        "config": {
                            "agent_id": "iris_integration",
                            "priority": "medium",
                            "timeout_ms": 5000,
                            "max_retries": 3,
                            "enable_cache": False,
                            "cache_ttl_seconds": 300,
                            "log_level": "INFO",
                        },
                        "input_data": {
                            "eye_vectors": [[0.5, 0.5]] * 120,
                            "frame_count": 120,
                            "fps": 24,
                        },
                    },
                )
                assert execute_response2.status_code == 200
                result2 = execute_response2.json()
                assert result2["score"] < 0.3  # Low liveness

            # Step 5: Verify stats updated again
            stats_response2 = client.get("/agents/iris_integration/stats")
            stats2 = stats_response2.json()
            assert stats2["execution_count"] == 2
