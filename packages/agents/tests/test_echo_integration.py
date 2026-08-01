"""
Integration tests for ECHO Agent with FastAPI service
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch

from src.api import app, register_agent
from src.agents.echo_agent import EchoAgent
from src.base import AgentConfig


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def echo_agent():
    """Create and register ECHO agent"""
    config = AgentConfig(
        agent_id="echo_integration",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )
    with patch.object(EchoAgent, "_find_wasm_path", return_value="/mock/path"):
        agent = EchoAgent(config)
        register_agent(agent)
        yield agent
        # Cleanup
        from src.api import agent_registry

        if "echo_integration" in agent_registry:
            del agent_registry["echo_integration"]


class TestEchoAgentAPIIntegration:
    """Integration tests for ECHO agent with FastAPI"""

    def test_execute_echo_via_api(self, client, echo_agent):
        """Test executing ECHO agent via API"""
        with patch.object(
            echo_agent,
            "_call_wasm_module",
            return_value={
                "delay_score": 25.5,
                "delay_ms": 12.5,
                "threshold_crossed": False,
                "signal_quality": 0.9,
            },
        ):
            response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "echo_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_samples": [0.1] * 1000,
                        "sample_rate": 44100,
                    },
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "echo_integration"
            assert data["status"] == "completed"
            assert 0.0 <= data["score"] <= 1.0
            assert 0.0 <= data["confidence"] <= 1.0
            assert "delay_score" in data["data"]
            assert data["data"]["delay_score"] == 25.5

    def test_execute_echo_invalid_input(self, client, echo_agent):
        """Test executing ECHO agent with invalid input via API"""
        response = client.post(
            "/execute",
            json={
                "config": {
                    "agent_id": "echo_integration",
                    "priority": "medium",
                    "timeout_ms": 5000,
                    "max_retries": 3,
                    "enable_cache": False,
                    "cache_ttl_seconds": 300,
                    "log_level": "INFO",
                },
                "input_data": {
                    "audio_samples": [0.1] * 50,  # Insufficient samples
                    "sample_rate": 44100,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error_message"] == "Input validation failed"

    def test_list_agents_includes_echo(self, client, echo_agent):
        """Test that ECHO agent appears in agent list"""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "echo_integration" in data["agents"]

    def test_get_echo_stats(self, client, echo_agent):
        """Test getting ECHO agent statistics"""
        # Execute agent once to generate stats
        with patch.object(
            echo_agent,
            "_call_wasm_module",
            return_value={
                "delay_score": 25.5,
                "delay_ms": 12.5,
                "threshold_crossed": False,
                "signal_quality": 0.9,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "echo_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_samples": [0.1] * 1000,
                        "sample_rate": 44100,
                    },
                },
            )

        # Get stats
        response = client.get("/agents/echo_integration/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "echo_integration"
        assert data["execution_count"] >= 1
        assert data["error_rate"] >= 0.0

    def test_reset_echo_stats(self, client, echo_agent):
        """Test resetting ECHO agent statistics"""
        # Execute agent once
        with patch.object(
            echo_agent,
            "_call_wasm_module",
            return_value={
                "delay_score": 25.5,
                "delay_ms": 12.5,
                "threshold_crossed": False,
                "signal_quality": 0.9,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "echo_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_samples": [0.1] * 1000,
                        "sample_rate": 44100,
                    },
                },
            )

        # Reset stats
        response = client.post("/agents/echo_integration/reset")
        assert response.status_code == 200
        data = response.json()
        assert "Statistics reset" in data["message"]

        # Verify stats are reset
        response = client.get("/agents/echo_integration/stats")
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
                    "audio_samples": [0.1] * 1000,
                    "sample_rate": 44100,
                },
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]


class TestEchoAgentEndToEnd:
    """End-to-end tests for ECHO agent workflow"""

    def test_full_echo_workflow(self, client, echo_agent):
        """Test complete ECHO agent workflow"""
        with patch.object(
            echo_agent,
            "_call_wasm_module",
            return_value={
                "delay_score": 25.5,
                "delay_ms": 12.5,
                "threshold_crossed": False,
                "signal_quality": 0.9,
            },
        ):
            # Step 1: Check agent is registered
            list_response = client.get("/agents")
            assert "echo_integration" in list_response.json()["agents"]

            # Step 2: Execute agent with valid data
            execute_response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "echo_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_samples": [0.1] * 2000,
                        "sample_rate": 44100,
                    },
                },
            )
            assert execute_response.status_code == 200
            result = execute_response.json()
            assert result["status"] == "completed"

            # Step 3: Verify stats updated
            stats_response = client.get("/agents/echo_integration/stats")
            stats = stats_response.json()
            assert stats["execution_count"] == 1

            # Step 4: Execute again with different data
            with patch.object(
                echo_agent,
                "_call_wasm_module",
                return_value={
                    "delay_score": 450.0,
                    "delay_ms": 250.0,
                    "threshold_crossed": True,
                    "signal_quality": 0.6,
                },
            ):
                execute_response2 = client.post(
                    "/execute",
                    json={
                        "config": {
                            "agent_id": "echo_integration",
                            "priority": "medium",
                            "timeout_ms": 5000,
                            "max_retries": 3,
                            "enable_cache": False,
                            "cache_ttl_seconds": 300,
                            "log_level": "INFO",
                        },
                        "input_data": {
                            "audio_samples": [0.2] * 1500,
                            "sample_rate": 48000,
                        },
                    },
                )
                assert execute_response2.status_code == 200
                result2 = execute_response2.json()
                assert result2["score"] > 0.7  # High delay

            # Step 5: Verify stats updated again
            stats_response2 = client.get("/agents/echo_integration/stats")
            stats2 = stats_response2.json()
            assert stats2["execution_count"] == 2
