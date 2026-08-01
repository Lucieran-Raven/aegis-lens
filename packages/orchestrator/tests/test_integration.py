"""
Integration Tests for Orchestrator

This module contains integration tests for the orchestrator API,
testing the full flow from agent results to verdicts and recommendations.
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch, AsyncMock

from src.orchestrator.api import app
from src.orchestrator.bayesian_engine import (
    BayesianEngine,
    AgentResult,
    AgentStatus,
    PriorParameters,
    AgentWeights,
)
from src.orchestrator.verdict import VerdictGenerator, VerdictStatus
from src.orchestrator.recommendation import RecommendationEngine


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_agent_results():
    """Sample agent results for testing"""
    return [
        {
            "agent_id": "chronos",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "data": {"mean_jitter": 15.0, "std_jitter": 3.0},
            "metadata": {"execution_time": 150},
        },
        {
            "agent_id": "echo",
            "status": "completed",
            "score": 0.75,
            "confidence": 0.85,
            "data": {"delay": 12.5},
            "metadata": {"execution_time": 120},
        },
        {
            "agent_id": "iris",
            "status": "completed",
            "score": 0.9,
            "confidence": 0.95,
            "data": {"liveness_score": 0.95},
            "metadata": {"execution_time": 200},
        },
        {
            "agent_id": "lipsync",
            "status": "completed",
            "score": 0.8,
            "confidence": 0.88,
            "data": {"sync_score": 0.85},
            "metadata": {"execution_time": 180},
        },
    ]


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"


class TestVerdictEndpoint:
    """Tests for verdict generation endpoint"""

    def test_generate_verdict_success(self, client, sample_agent_results):
        """Test successful verdict generation"""
        response = client.post(
            "/verdict",
            json={
                "agent_results": sample_agent_results,
                "history": [0.6, 0.65, 0.7, 0.75, 0.8],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "trust_score" in data
        assert 0.0 <= data["trust_score"] <= 1.0
        assert "confidence" in data
        assert "reasoning" in data
        assert data["evidence_count"] == 4
        assert isinstance(data["evidence"], list)
        assert len(data["evidence"]) == 4

    def test_generate_verdict_no_history(self, client, sample_agent_results):
        """Test verdict generation without history"""
        response = client.post(
            "/verdict",
            json={"agent_results": sample_agent_results},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_trend"] is False
        assert data["trend"] is None

    def test_generate_verdict_custom_priors(self, client, sample_agent_results):
        """Test verdict generation with custom priors"""
        response = client.post(
            "/verdict",
            json={
                "agent_results": sample_agent_results,
                "priors": {
                    "alpha": 3.0,
                    "beta": 2.0,
                    "base_reliability": 0.8,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data

    def test_generate_verdict_custom_weights(self, client, sample_agent_results):
        """Test verdict generation with custom weights"""
        response = client.post(
            "/verdict",
            json={
                "agent_results": sample_agent_results,
                "weights": {
                    "chronos": 0.3,
                    "echo": 0.2,
                    "iris": 0.3,
                    "lipsync": 0.2,
                    "nova": 0.0,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data

    def test_generate_verdict_invalid_status(self, client, sample_agent_results):
        """Test verdict generation with invalid agent status"""
        invalid_results = sample_agent_results.copy()
        invalid_results[0]["status"] = "invalid_status"

        response = client.post(
            "/verdict",
            json={"agent_results": invalid_results},
        )

        # Pydantic validation returns 422
        assert response.status_code == 422

    def test_generate_verdict_invalid_score(self, client, sample_agent_results):
        """Test verdict generation with invalid score"""
        invalid_results = sample_agent_results.copy()
        invalid_results[0]["score"] = 1.5  # Invalid: > 1.0

        response = client.post(
            "/verdict",
            json={"agent_results": invalid_results},
        )

        assert response.status_code == 422  # Validation error

    def test_generate_verdict_empty_results(self, client):
        """Test verdict generation with empty agent results"""
        response = client.post(
            "/verdict",
            json={"agent_results": []},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["evidence_count"] == 0


class TestRecommendationEndpoint:
    """Tests for recommendation generation endpoint"""

    def test_generate_recommendations_success(self, client, sample_agent_results):
        """Test successful recommendation generation"""
        response = client.post(
            "/recommendations",
            json={
                "agent_results": sample_agent_results,
                "history": [0.6, 0.65, 0.7, 0.75, 0.8],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "verdict_status" in data
        assert "trust_score" in data
        assert "risk_level" in data
        assert "summary" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert "suggested_interview_flow" in data

    def test_generate_recommendations_low_trust(self, client):
        """Test recommendations with low trust scores"""
        low_trust_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.2,
                "confidence": 0.8,
                "data": {},
                "metadata": {},
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.15,
                "confidence": 0.75,
                "data": {},
                "metadata": {},
            },
        ]

        response = client.post(
            "/recommendations",
            json={"agent_results": low_trust_results},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["HIGH", "MEDIUM"]
        assert len(data["recommendations"]) > 0

    def test_generate_recommendations_high_trust(self, client, sample_agent_results):
        """Test recommendations with high trust scores"""
        response = client.post(
            "/recommendations",
            json={"agent_results": sample_agent_results},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["LOW", "MEDIUM"]


class TestFullAnalysisEndpoint:
    """Tests for full analysis endpoint"""

    def test_full_analysis_success(self, client, sample_agent_results):
        """Test full analysis endpoint"""
        response = client.post(
            "/analyze",
            json={
                "agent_results": sample_agent_results,
                "history": [0.6, 0.65, 0.7, 0.75, 0.8],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "verdict" in data
        assert "recommendations" in data

        # Check verdict structure
        assert "status" in data["verdict"]
        assert "trust_score" in data["verdict"]
        assert "evidence" in data["verdict"]

        # Check recommendations structure
        assert "verdict_status" in data["recommendations"]
        assert "risk_level" in data["recommendations"]
        assert "recommendations" in data["recommendations"]


class TestConfigurationEndpoints:
    """Tests for configuration endpoints"""

    def test_get_priors(self, client):
        """Test getting current priors"""
        response = client.get("/config/priors")
        assert response.status_code == 200
        data = response.json()
        assert "alpha" in data
        assert "beta" in data
        assert "base_reliability" in data

    def test_update_priors(self, client):
        """Test updating priors"""
        response = client.post(
            "/config/priors",
            json={
                "alpha": 3.0,
                "beta": 2.0,
                "base_reliability": 0.8,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify update
        get_response = client.get("/config/priors")
        assert get_response.json()["alpha"] == 3.0

    def test_get_weights(self, client):
        """Test getting current weights"""
        response = client.get("/config/weights")
        assert response.status_code == 200
        data = response.json()
        assert "chronos" in data
        assert "echo" in data
        assert "iris" in data
        assert "lipsync" in data
        assert "nova" in data

    def test_update_weights(self, client):
        """Test updating weights"""
        response = client.post(
            "/config/weights",
            json={
                "chronos": 0.3,
                "echo": 0.2,
                "iris": 0.3,
                "lipsync": 0.2,
                "nova": 0.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestBayesianEngineIntegration:
    """Integration tests for Bayesian Engine"""

    def test_full_bayesian_flow(self):
        """Test full Bayesian engine flow"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)

        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.85,
                confidence=0.9,
                data={"mean_jitter": 15.0},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.75,
                confidence=0.85,
                data={"delay": 12.5},
                metadata={},
            ),
        ]

        # Calculate trust score
        trust_score, metadata = engine.calculate_trust_score(results)
        assert 0.0 <= trust_score <= 1.0

        # Generate verdict
        verdict = verdict_gen.generate_verdict(results)
        assert verdict.status in [
            VerdictStatus.CLEAR,
            VerdictStatus.SUSPECT,
            VerdictStatus.LIKELY_FAKE,
        ]
        assert 0.0 <= verdict.trust_score <= 1.0


class TestRecommendationEngineIntegration:
    """Integration tests for Recommendation Engine"""

    def test_full_recommendation_flow(self):
        """Test full recommendation engine flow"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)
        rec_engine = RecommendationEngine()

        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.2,
                confidence=0.8,
                data={"mean_jitter": 50.0},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.15,
                confidence=0.75,
                data={"delay": 100.0},
                metadata={},
            ),
        ]

        # Generate verdict
        verdict = verdict_gen.generate_verdict(results)

        # Generate recommendations
        report = rec_engine.generate_recommendations(verdict)
        assert report.verdict_status == verdict.status
        assert len(report.recommendations) > 0
        assert report.risk_level in ["HIGH", "MEDIUM", "LOW"]


class TestEndToEndFlow:
    """End-to-end integration tests"""

    def test_complete_flow_low_trust(self, client):
        """Test complete flow with low trust scenario"""
        low_trust_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.2,
                "confidence": 0.8,
                "data": {"mean_jitter": 50.0},
                "metadata": {},
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.15,
                "confidence": 0.75,
                "data": {"delay": 100.0},
                "metadata": {},
            },
        ]

        # Update configuration
        client.post(
            "/config/priors",
            json={"alpha": 2.0, "beta": 1.0, "base_reliability": 0.7},
        )

        # Generate verdict
        verdict_response = client.post(
            "/verdict",
            json={"agent_results": low_trust_results},
        )
        assert verdict_response.status_code == 200
        verdict_data = verdict_response.json()

        # Generate recommendations
        rec_response = client.post(
            "/recommendations",
            json={"agent_results": low_trust_results},
        )
        assert rec_response.status_code == 200
        rec_data = rec_response.json()

        # Verify consistency
        assert verdict_data["status"] == rec_data["verdict_status"]
        assert verdict_data["trust_score"] == rec_data["trust_score"]

    def test_complete_flow_high_trust(self, client, sample_agent_results):
        """Test complete flow with high trust scenario"""
        # Generate verdict
        verdict_response = client.post(
            "/verdict",
            json={"agent_results": sample_agent_results},
        )
        assert verdict_response.status_code == 200

        # Generate recommendations
        rec_response = client.post(
            "/recommendations",
            json={"agent_results": sample_agent_results},
        )
        assert rec_response.status_code == 200

        # Full analysis
        analysis_response = client.post(
            "/analyze",
            json={"agent_results": sample_agent_results},
        )
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()

        # Verify all components present
        assert "verdict" in analysis_data
        assert "recommendations" in analysis_data
        assert (
            analysis_data["verdict"]["status"] == analysis_data["recommendations"]["verdict_status"]
        )
