"""
Unit tests for Bayesian Engine
"""

import pytest
import numpy as np
from orchestrator.bayesian_engine import (
    BayesianEngine,
    AgentResult,
    AgentStatus,
    PriorParameters,
    AgentWeights,
)


@pytest.fixture
def bayesian_engine():
    """Create Bayesian Engine instance"""
    return BayesianEngine()


@pytest.fixture
def sample_results():
    """Create sample agent results"""
    return [
        AgentResult(
            agent_id="chronos",
            status=AgentStatus.COMPLETED,
            score=0.85,
            confidence=0.9,
            data={"mean_jitter": 15.0, "std_jitter": 3.0},
            metadata={"execution_time": 100},
        ),
        AgentResult(
            agent_id="echo",
            status=AgentStatus.COMPLETED,
            score=0.75,
            confidence=0.85,
            data={"delay": 12.5},
            metadata={"execution_time": 150},
        ),
        AgentResult(
            agent_id="iris",
            status=AgentStatus.COMPLETED,
            score=0.90,
            confidence=0.95,
            data={"liveness_score": 0.95},
            metadata={"execution_time": 200},
        ),
        AgentResult(
            agent_id="lipsync",
            status=AgentStatus.COMPLETED,
            score=0.80,
            confidence=0.88,
            data={"sync_score": 0.85},
            metadata={"execution_time": 180},
        ),
    ]


class TestBayesianEngineInitialization:
    """Tests for Bayesian Engine initialization"""

    def test_default_initialization(self):
        """Test initialization with default priors"""
        engine = BayesianEngine()
        assert engine.priors.alpha == 2.0
        assert engine.priors.beta == 1.0
        assert engine.priors.base_reliability == 0.7

    def test_custom_priors(self):
        """Test initialization with custom priors"""
        priors = PriorParameters(alpha=5.0, beta=2.0, base_reliability=0.8)
        engine = BayesianEngine(priors)
        assert engine.priors.alpha == 5.0
        assert engine.priors.beta == 2.0
        assert engine.priors.base_reliability == 0.8


class TestPriorParameters:
    """Tests for prior parameter management"""

    def test_update_priors(self, bayesian_engine):
        """Test updating prior parameters"""
        bayesian_engine.update_priors(alpha=3.0, beta=1.5, base_reliability=0.75)
        assert bayesian_engine.priors.alpha == 3.0
        assert bayesian_engine.priors.beta == 1.5
        assert bayesian_engine.priors.base_reliability == 0.75


class TestAgentWeights:
    """Tests for agent weight management"""

    def test_default_weights(self, bayesian_engine):
        """Test default agent weights"""
        assert bayesian_engine.weights.chronos == 0.25
        assert bayesian_engine.weights.echo == 0.20
        assert bayesian_engine.weights.iris == 0.25
        assert bayesian_engine.weights.lipsync == 0.20
        assert bayesian_engine.weights.nova == 0.10

    def test_set_agent_weights(self, bayesian_engine):
        """Test setting custom agent weights"""
        weights = AgentWeights(chronos=0.30, echo=0.25, iris=0.20, lipsync=0.15, nova=0.10)
        bayesian_engine.set_agent_weights(weights)
        assert bayesian_engine.weights.chronos == 0.30
        assert bayesian_engine.weights.echo == 0.25

    def test_get_agent_weight(self, bayesian_engine):
        """Test getting weight for specific agent"""
        assert bayesian_engine._get_agent_weight("chronos") == 0.25
        assert bayesian_engine._get_agent_weight("echo") == 0.20
        assert bayesian_engine._get_agent_weight("unknown") == 0.1


class TestWeightedScoreCalculation:
    """Tests for weighted score calculation"""

    def test_calculate_weighted_score(self, bayesian_engine, sample_results):
        """Test weighted score calculation"""
        score, contributions = bayesian_engine.calculate_weighted_score(sample_results)
        assert 0.0 <= score <= 1.0
        assert "chronos" in contributions
        assert "echo" in contributions
        assert "iris" in contributions
        assert "lipsync" in contributions

    def test_calculate_weighted_score_empty(self, bayesian_engine):
        """Test weighted score with empty results"""
        score, contributions = bayesian_engine.calculate_weighted_score([])
        assert score == 0.5
        assert contributions == {}

    def test_calculate_weighted_score_with_pending(self, bayesian_engine):
        """Test weighted score with pending agents"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.PENDING,
                score=0.0,
                confidence=0.0,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        score, contributions = bayesian_engine.calculate_weighted_score(results)
        assert "chronos" not in contributions
        assert "echo" in contributions


class TestBetaPosteriorCalculation:
    """Tests for Beta posterior calculation"""

    def test_calculate_beta_posterior(self, bayesian_engine, sample_results):
        """Test Beta posterior calculation"""
        alpha, beta, expected = bayesian_engine.calculate_beta_posterior(sample_results)
        assert alpha > bayesian_engine.priors.alpha  # Positive evidence increases alpha
        # Beta may or may not increase depending on scores
        assert beta >= bayesian_engine.priors.beta
        assert 0.0 <= expected <= 1.0

    def test_calculate_beta_posterior_empty(self, bayesian_engine):
        """Test Beta posterior with empty results"""
        alpha, beta, expected = bayesian_engine.calculate_beta_posterior([])
        assert alpha == bayesian_engine.priors.alpha
        assert beta == bayesian_engine.priors.beta
        assert expected == alpha / (alpha + beta)

    def test_calculate_beta_posterior_high_scores(self, bayesian_engine):
        """Test Beta posterior with high scores (positive evidence)"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.9,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.95,
                confidence=0.95,
                data={},
                metadata={},
            ),
        ]
        alpha, beta, expected = bayesian_engine.calculate_beta_posterior(results)
        assert alpha > beta  # More positive evidence
        assert expected > 0.7

    def test_calculate_beta_posterior_low_scores(self, bayesian_engine):
        """Test Beta posterior with low scores (negative evidence)"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.1,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.05,
                confidence=0.95,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.1,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        alpha, beta, expected = bayesian_engine.calculate_beta_posterior(results)
        # Low scores increase beta more than alpha
        assert beta > bayesian_engine.priors.beta
        # With very low scores and more agents, expected should be lower
        assert expected < 0.6


class TestCredibilityInterval:
    """Tests for credibility interval calculation"""

    def test_calculate_credibility_interval(self, bayesian_engine):
        """Test credibility interval calculation"""
        lower, upper = bayesian_engine.calculate_credibility_interval(alpha=10, beta=5)
        assert 0.0 <= lower <= upper <= 1.0
        assert lower < upper

    def test_calculate_credibility_interval_custom_confidence(self, bayesian_engine):
        """Test credibility interval with custom confidence"""
        lower_95, upper_95 = bayesian_engine.calculate_credibility_interval(
            alpha=10, beta=5, confidence=0.95
        )
        lower_90, upper_90 = bayesian_engine.calculate_credibility_interval(
            alpha=10, beta=5, confidence=0.90
        )
        # 90% interval should be narrower than 95%
        assert (upper_90 - lower_90) < (upper_95 - lower_95)


class TestTrustScoreCalculation:
    """Tests for trust score calculation"""

    def test_calculate_trust_score(self, bayesian_engine, sample_results):
        """Test trust score calculation"""
        score, metadata = bayesian_engine.calculate_trust_score(sample_results)
        assert 0.0 <= score <= 1.0
        assert "weighted_score" in metadata
        assert "bayesian_expected" in metadata
        assert "alpha_posterior" in metadata
        assert "beta_posterior" in metadata
        assert "credibility_interval" in metadata
        assert "contributions" in metadata
        assert "agent_count" in metadata

    def test_calculate_trust_score_high_confidence(self, bayesian_engine):
        """Test trust score with high confidence results"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.9,
                confidence=0.95,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.95,
                confidence=0.95,
                data={},
                metadata={},
            ),
        ]
        score, _ = bayesian_engine.calculate_trust_score(results)
        assert score >= 0.7  # Should be high

    def test_calculate_trust_score_low_confidence(self, bayesian_engine):
        """Test trust score with low confidence results"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.2,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.15,
                confidence=0.95,
                data={},
                metadata={},
            ),
        ]
        score, _ = bayesian_engine.calculate_trust_score(results)
        assert score <= 0.5  # Should be low


class TestStatusDetermination:
    """Tests for status determination"""

    def test_determine_status_clear(self, bayesian_engine):
        """Test CLEAR status determination"""
        assert bayesian_engine.determine_status(0.85) == "CLEAR"
        assert bayesian_engine.determine_status(0.9) == "CLEAR"

    def test_determine_status_suspect(self, bayesian_engine):
        """Test SUSPECT status determination"""
        assert bayesian_engine.determine_status(0.6) == "SUSPECT"
        assert bayesian_engine.determine_status(0.7) == "SUSPECT"

    def test_determine_status_likely_fake(self, bayesian_engine):
        """Test LIKELY_FAKE status determination"""
        assert bayesian_engine.determine_status(0.4) == "LIKELY_FAKE"
        assert bayesian_engine.determine_status(0.35) == "LIKELY_FAKE"

    def test_determine_status_fake(self, bayesian_engine):
        """Test FAKE status determination"""
        assert bayesian_engine.determine_status(0.2) == "FAKE"
        assert bayesian_engine.determine_status(0.1) == "FAKE"


class TestAnomalyDetection:
    """Tests for anomaly detection"""

    def test_detect_anomaly_none(self, bayesian_engine, sample_results):
        """Test no anomaly detection"""
        anomaly = bayesian_engine.detect_anomaly(sample_results, trust_score=0.8)
        assert anomaly is None

    def test_detect_anomaly_high_variance(self, bayesian_engine):
        """Test high variance anomaly detection"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.9,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.2,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        anomaly = bayesian_engine.detect_anomaly(results, trust_score=0.5)
        assert anomaly is not None
        assert anomaly["type"] == "HIGH_VARIANCE"

    def test_detect_anomaly_outlier(self, bayesian_engine):
        """Test outlier agent detection"""
        # Use many agents with very close scores and one extreme outlier
        # This ensures low variance but high z-score for the outlier
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.75,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.76,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.05,  # Extreme outlier
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="lipsync",
                status=AgentStatus.COMPLETED,
                score=0.74,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="nova",
                status=AgentStatus.COMPLETED,
                score=0.75,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="sentient",
                status=AgentStatus.COMPLETED,
                score=0.76,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="aura",
                status=AgentStatus.COMPLETED,
                score=0.75,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        anomaly = bayesian_engine.detect_anomaly(results, trust_score=0.6)
        assert anomaly is not None
        assert anomaly["type"] == "OUTLIER_AGENT"
        assert anomaly["agent_id"] == "iris"

    def test_detect_anomaly_insufficient_data(self, bayesian_engine):
        """Test anomaly detection with insufficient data"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            )
        ]
        anomaly = bayesian_engine.detect_anomaly(results, trust_score=0.8)
        assert anomaly is None


class TestTrendAnalysis:
    """Tests for trend analysis"""

    def test_analyze_trend_insufficient_data(self, bayesian_engine):
        """Test trend analysis with insufficient data"""
        trend = bayesian_engine.analyze_trend([0.5])
        assert trend["trend"] == "INSUFFICIENT_DATA"
        assert trend["slope"] == 0.0

    def test_analyze_trend_improving(self, bayesian_engine):
        """Test improving trend detection"""
        history = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        trend = bayesian_engine.analyze_trend(history)
        assert trend["trend"] == "IMPROVING"
        assert trend["slope"] > 0

    def test_analyze_trend_declining(self, bayesian_engine):
        """Test declining trend detection"""
        history = [0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5]
        trend = bayesian_engine.analyze_trend(history)
        assert trend["trend"] == "DECLINING"
        assert trend["slope"] < 0

    def test_analyze_trend_stable(self, bayesian_engine):
        """Test stable trend detection"""
        history = [0.7, 0.71, 0.69, 0.7, 0.7, 0.71, 0.7]
        trend = bayesian_engine.analyze_trend(history)
        assert trend["trend"] == "STABLE"
        assert abs(trend["slope"]) < 0.01

    def test_analyze_trend_window_size(self, bayesian_engine):
        """Test trend analysis with custom window size"""
        history = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.5, 0.5, 0.5, 0.5, 0.5]
        trend = bayesian_engine.analyze_trend(history, window_size=5)
        # Should only consider last 5 values
        assert trend["current"] == 0.5
        assert trend["average"] < 0.6
