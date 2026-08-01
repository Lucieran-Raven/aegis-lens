"""
Integration tests for LIPSYNC Agent with FastAPI service
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch

from src.api import app, register_agent
from src.agents.lipsync_agent import LipsyncAgent
from src.base import AgentConfig


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def lipsync_agent():
    """Create and register LIPSYNC agent"""
    config = AgentConfig(
        agent_id="lipsync_integration",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )
    with patch.object(LipsyncAgent, "_find_wasm_path", return_value="/mock/path"):
        agent = LipsyncAgent(config)
        register_agent(agent)
        yield agent
        # Cleanup
        from src.api import agent_registry

        if "lipsync_integration" in agent_registry:
            del agent_registry["lipsync_integration"]


class TestLipsyncAgentAPIIntegration:
    """Integration tests for LIPSYNC agent with FastAPI"""

    def test_execute_lipsync_via_api(self, client, lipsync_agent):
        """Test executing LIPSYNC agent via API"""
        with patch.object(
            lipsync_agent,
            "_call_wasm_module",
            return_value={
                "sync_score": 85.5,
                "sync_error": 15.2,
                "phoneme_match_rate": 0.9,
                "mouth_openness_variance": 25.0,
            },
        ):
            response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "lipsync_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_features": [[0.1, 0.2, 0.3]] * 100,
                        "video_features": [[0.4, 0.5, 0.6]] * 100,
                        "sync_data": [[0, 10]] * 100,
                    },
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "lipsync_integration"
            assert data["status"] == "completed"
            assert 0.0 <= data["score"] <= 1.0
            assert 0.0 <= data["confidence"] <= 1.0
            assert "sync_score" in data["data"]
            assert data["data"]["sync_score"] == 85.5

    def test_execute_lipsync_invalid_input(self, client, lipsync_agent):
        """Test executing LIPSYNC agent with invalid input via API"""
        response = client.post(
            "/execute",
            json={
                "config": {
                    "agent_id": "lipsync_integration",
                    "priority": "medium",
                    "timeout_ms": 5000,
                    "max_retries": 3,
                    "enable_cache": False,
                    "cache_ttl_seconds": 300,
                    "log_level": "INFO",
                },
                "input_data": {
                    "audio_features": [[0.1, 0.2, 0.3]] * 5,  # Insufficient features
                    "video_features": [[0.4, 0.5, 0.6]] * 5,
                    "sync_data": [[0, 10]] * 5,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error_message"] == "Input validation failed"

    def test_list_agents_includes_lipsync(self, client, lipsync_agent):
        """Test that LIPSYNC agent appears in agent list"""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "lipsync_integration" in data["agents"]

    def test_get_lipsync_stats(self, client, lipsync_agent):
        """Test getting LIPSYNC agent statistics"""
        # Execute agent once to generate stats
        with patch.object(
            lipsync_agent,
            "_call_wasm_module",
            return_value={
                "sync_score": 85.5,
                "sync_error": 15.2,
                "phoneme_match_rate": 0.9,
                "mouth_openness_variance": 25.0,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "lipsync_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_features": [[0.1, 0.2, 0.3]] * 100,
                        "video_features": [[0.4, 0.5, 0.6]] * 100,
                        "sync_data": [[0, 10]] * 100,
                    },
                },
            )

        # Get stats
        response = client.get("/agents/lipsync_integration/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "lipsync_integration"
        assert data["execution_count"] >= 1
        assert data["error_rate"] >= 0.0

    def test_reset_lipsync_stats(self, client, lipsync_agent):
        """Test resetting LIPSYNC agent statistics"""
        # Execute agent once
        with patch.object(
            lipsync_agent,
            "_call_wasm_module",
            return_value={
                "sync_score": 85.5,
                "sync_error": 15.2,
                "phoneme_match_rate": 0.9,
                "mouth_openness_variance": 25.0,
            },
        ):
            client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "lipsync_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_features": [[0.1, 0.2, 0.3]] * 100,
                        "video_features": [[0.4, 0.5, 0.6]] * 100,
                        "sync_data": [[0, 10]] * 100,
                    },
                },
            )

        # Reset stats
        response = client.post("/agents/lipsync_integration/reset")
        assert response.status_code == 200
        data = response.json()
        assert "Statistics reset" in data["message"]

        # Verify stats are reset
        response = client.get("/agents/lipsync_integration/stats")
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
                    "audio_features": [[0.1, 0.2, 0.3]] * 100,
                    "video_features": [[0.4, 0.5, 0.6]] * 100,
                    "sync_data": [[0, 10]] * 100,
                },
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]


class TestLipsyncAgentEndToEnd:
    """End-to-end tests for LIPSYNC agent workflow"""

    def test_full_lipsync_workflow(self, client, lipsync_agent):
        """Test complete LIPSYNC agent workflow"""
        with patch.object(
            lipsync_agent,
            "_call_wasm_module",
            return_value={
                "sync_score": 85.5,
                "sync_error": 15.2,
                "phoneme_match_rate": 0.9,
                "mouth_openness_variance": 25.0,
            },
        ):
            # Step 1: Check agent is registered
            list_response = client.get("/agents")
            assert "lipsync_integration" in list_response.json()["agents"]

            # Step 2: Execute agent with valid data
            execute_response = client.post(
                "/execute",
                json={
                    "config": {
                        "agent_id": "lipsync_integration",
                        "priority": "medium",
                        "timeout_ms": 5000,
                        "max_retries": 3,
                        "enable_cache": False,
                        "cache_ttl_seconds": 300,
                        "log_level": "INFO",
                    },
                    "input_data": {
                        "audio_features": [[0.1, 0.2, 0.3]] * 150,
                        "video_features": [[0.4, 0.5, 0.6]] * 150,
                        "sync_data": [[0, 10]] * 150,
                    },
                },
            )
            assert execute_response.status_code == 200
            result = execute_response.json()
            assert result["status"] == "completed"

            # Step 3: Verify stats updated
            stats_response = client.get("/agents/lipsync_integration/stats")
            stats = stats_response.json()
            assert stats["execution_count"] == 1

            # Step 4: Execute again with different data
            with patch.object(
                lipsync_agent,
                "_call_wasm_module",
                return_value={
                    "sync_score": 15.0,
                    "sync_error": 75.0,
                    "phoneme_match_rate": 0.3,
                    "mouth_openness_variance": 120.0,
                },
            ):
                execute_response2 = client.post(
                    "/execute",
                    json={
                        "config": {
                            "agent_id": "lipsync_integration",
                            "priority": "medium",
                            "timeout_ms": 5000,
                            "max_retries": 3,
                            "enable_cache": False,
                            "cache_ttl_seconds": 300,
                            "log_level": "INFO",
                        },
                        "input_data": {
                            "audio_features": [[0.2, 0.3, 0.4]] * 120,
                            "video_features": [[0.5, 0.6, 0.7]] * 120,
                            "sync_data": [[0, 12]] * 120,
                        },
                    },
                )
                assert execute_response2.status_code == 200
                result2 = execute_response2.json()
                assert result2["score"] < 0.3  # Low sync

            # Step 5: Verify stats updated again
            stats_response2 = client.get("/agents/lipsync_integration/stats")
            stats2 = stats_response2.json()
            assert stats2["execution_count"] == 2
