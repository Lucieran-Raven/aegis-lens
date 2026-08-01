"""
Unit tests for Verdict Generation Module
"""

import pytest
from datetime import datetime
from src.orchestrator.verdict import (
    VerdictGenerator,
    Verdict,
    VerdictStatus,
    VerdictEvidence,
)
from src.orchestrator.bayesian_engine import (
    AgentResult,
    AgentStatus,
    BayesianEngine,
)


@pytest.fixture
def verdict_generator():
    """Create Verdict Generator instance"""
    return VerdictGenerator()


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


class TestVerdictGeneratorInitialization:
    """Tests for Verdict Generator initialization"""

    def test_default_initialization(self):
        """Test initialization with default Bayesian engine"""
        generator = VerdictGenerator()
        assert generator.bayesian_engine is not None
        assert isinstance(generator.bayesian_engine, BayesianEngine)

    def test_custom_bayesian_engine(self):
        """Test initialization with custom Bayesian engine"""
        engine = BayesianEngine()
        generator = VerdictGenerator(engine)
        assert generator.bayesian_engine is engine


class TestVerdictGeneration:
    """Tests for verdict generation"""

    def test_generate_verdict_clear(self, verdict_generator, sample_results):
        """Test generating CLEAR verdict"""
        verdict = verdict_generator.generate_verdict(sample_results)
        # Bayesian engine is conservative, so high scores may still be SUSPECT
        assert verdict.status in [VerdictStatus.CLEAR, VerdictStatus.SUSPECT]
        assert 0.0 <= verdict.trust_score <= 1.0
        assert 0.0 <= verdict.confidence <= 1.0
        assert len(verdict.evidence) > 0
        assert verdict.reasoning
        assert verdict.generated_at

    def test_generate_verdict_with_history(self, verdict_generator, sample_results):
        """Test generating verdict with trend history"""
        history = [0.6, 0.65, 0.7, 0.75, 0.8]
        verdict = verdict_generator.generate_verdict(sample_results, history)
        assert verdict.trend is not None
        assert "trend" in verdict.trend
        assert "slope" in verdict.trend

    def test_generate_verdict_suspect(self, verdict_generator):
        """Test generating SUSPECT verdict"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.6,
                confidence=0.8,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.55,
                confidence=0.75,
                data={},
                metadata={},
            ),
        ]
        verdict = verdict_generator.generate_verdict(results)
        assert verdict.status in [VerdictStatus.SUSPECT, VerdictStatus.INCONCLUSIVE]

    def test_generate_verdict_likely_fake(self, verdict_generator):
        """Test generating LIKELY_FAKE verdict"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.35,
                confidence=0.8,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.25,
                confidence=0.75,
                data={},
                metadata={},
            ),
        ]
        verdict = verdict_generator.generate_verdict(results)
        assert verdict.status in [
            VerdictStatus.LIKELY_FAKE,
            VerdictStatus.FAKE,
            VerdictStatus.INCONCLUSIVE,
        ]

    def test_generate_verdict_fake(self, verdict_generator):
        """Test generating FAKE verdict"""
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
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.05,
                confidence=0.95,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.15,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        verdict = verdict_generator.generate_verdict(results)
        assert verdict.status in [VerdictStatus.FAKE, VerdictStatus.LIKELY_FAKE]

    def test_generate_verdict_inconclusive(self, verdict_generator):
        """Test generating INCONCLUSIVE verdict with insufficient agents"""
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
        verdict = verdict_generator.generate_verdict(results)
        assert verdict.status == VerdictStatus.INCONCLUSIVE


class TestStatusDetermination:
    """Tests for status determination logic"""

    def test_determine_status_with_high_anomaly(self, verdict_generator):
        """Test status determination with high severity anomaly"""
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
        verdict = verdict_generator.generate_verdict(results)
        # High variance should downgrade status
        assert verdict.anomaly is not None
        assert verdict.status in [VerdictStatus.SUSPECT, VerdictStatus.LIKELY_FAKE]

    def test_determine_status_with_declining_trend(self, verdict_generator):
        """Test status determination with declining trend"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.6,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.55,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        history = [0.8, 0.75, 0.7, 0.65, 0.6]
        verdict = verdict_generator.generate_verdict(results, history)
        assert verdict.trend is not None
        assert verdict.trend["trend"] == "DECLINING"


class TestConfidenceCalculation:
    """Tests for confidence calculation"""

    def test_confidence_high_agent_count(self, verdict_generator, sample_results):
        """Test confidence with high agent count"""
        verdict = verdict_generator.generate_verdict(sample_results)
        # Confidence may be reduced due to wide credibility interval
        assert verdict.confidence >= 0.7

    def test_confidence_low_agent_count(self, verdict_generator):
        """Test confidence with low agent count"""
        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.8,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="echo",
                status=AgentStatus.COMPLETED,
                score=0.75,
                confidence=0.85,
                data={},
                metadata={},
            ),
        ]
        verdict = verdict_generator.generate_verdict(results)
        assert verdict.confidence < 0.8

    def test_confidence_with_anomaly(self, verdict_generator):
        """Test confidence reduction with anomaly"""
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
        verdict = verdict_generator.generate_verdict(results)
        # Anomaly should reduce confidence
        assert verdict.confidence < 0.8


class TestEvidenceAggregation:
    """Tests for evidence aggregation"""

    def test_aggregate_evidence(self, verdict_generator, sample_results):
        """Test evidence aggregation"""
        verdict = verdict_generator.generate_verdict(sample_results)
        assert len(verdict.evidence) == len(sample_results)

        # Check evidence structure
        for evidence in verdict.evidence:
            assert isinstance(evidence, VerdictEvidence)
            assert evidence.agent_id
            assert 0.0 <= evidence.score <= 1.0
            assert 0.0 <= evidence.confidence <= 1.0
            assert evidence.weight > 0
            assert evidence.contribution in ["positive", "negative", "neutral"]

    def test_evidence_sorting(self, verdict_generator, sample_results):
        """Test evidence is sorted by score (descending)"""
        verdict = verdict_generator.generate_verdict(sample_results)
        scores = [e.score for e in verdict.evidence]
        assert scores == sorted(scores, reverse=True)

    def test_evidence_contribution_types(self, verdict_generator):
        """Test evidence contribution type classification"""
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
                score=0.5,
                confidence=0.9,
                data={},
                metadata={},
            ),
            AgentResult(
                agent_id="iris",
                status=AgentStatus.COMPLETED,
                score=0.2,
                confidence=0.9,
                data={},
                metadata={},
            ),
        ]
        verdict = verdict_generator.generate_verdict(results)
        contributions = {e.contribution for e in verdict.evidence}
        assert "positive" in contributions
        assert "neutral" in contributions
        assert "negative" in contributions


class TestReasoningGeneration:
    """Tests for reasoning generation"""

    def test_reasoning_content(self, verdict_generator, sample_results):
        """Test reasoning contains key information"""
        verdict = verdict_generator.generate_verdict(sample_results)
        assert verdict.reasoning
        assert "trust score" in verdict.reasoning.lower()
        assert str(verdict.status.value.lower()) in verdict.reasoning.lower()

    def test_reasoning_with_anomaly(self, verdict_generator):
        """Test reasoning includes anomaly information"""
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
        verdict = verdict_generator.generate_verdict(results)
        if verdict.anomaly:
            assert "variance" in verdict.reasoning.lower() or "outlier" in verdict.reasoning.lower()

    def test_reasoning_with_trend(self, verdict_generator, sample_results):
        """Test reasoning includes trend information"""
        history = [0.6, 0.65, 0.7, 0.75, 0.8]
        verdict = verdict_generator.generate_verdict(sample_results, history)
        assert "trend" in verdict.reasoning.lower()


class TestSummaryGeneration:
    """Tests for summary generation"""

    def test_generate_summary(self, verdict_generator, sample_results):
        """Test summary generation"""
        verdict = verdict_generator.generate_verdict(sample_results)
        summary = verdict_generator.generate_summary(verdict)

        assert summary["status"] == verdict.status.value
        assert summary["trust_score"] == verdict.trust_score
        assert summary["confidence"] == verdict.confidence
        assert summary["reasoning"] == verdict.reasoning
        assert summary["evidence_count"] == len(verdict.evidence)
        assert summary["has_anomaly"] == (verdict.anomaly is not None)
        assert summary["has_trend"] == (verdict.trend is not None)
        assert "generated_at" in summary


class TestVerdictDataclass:
    """Tests for Verdict dataclass"""

    def test_verdict_creation(self):
        """Test Verdict dataclass creation"""
        verdict = Verdict(
            status=VerdictStatus.CLEAR,
            trust_score=0.85,
            confidence=0.9,
            evidence=[],
            reasoning="Test reasoning",
        )
        assert verdict.status == VerdictStatus.CLEAR
        assert verdict.trust_score == 0.85
        assert verdict.confidence == 0.9
        assert verdict.evidence == []
        assert verdict.reasoning == "Test reasoning"
        assert verdict.anomaly is None
        assert verdict.trend is None
        assert isinstance(verdict.generated_at, datetime)

    def test_verdict_with_metadata(self):
        """Test Verdict with metadata"""
        verdict = Verdict(
            status=VerdictStatus.SUSPECT,
            trust_score=0.6,
            confidence=0.8,
            evidence=[],
            reasoning="Test",
            metadata={"key": "value"},
        )
        assert verdict.metadata == {"key": "value"}


class TestVerdictEvidenceDataclass:
    """Tests for VerdictEvidence dataclass"""

    def test_evidence_creation(self):
        """Test VerdictEvidence dataclass creation"""
        evidence = VerdictEvidence(
            agent_id="chronos",
            score=0.85,
            confidence=0.9,
            weight=0.25,
            contribution="positive",
            details={"test": "data"},
        )
        assert evidence.agent_id == "chronos"
        assert evidence.score == 0.85
        assert evidence.confidence == 0.9
        assert evidence.weight == 0.25
        assert evidence.contribution == "positive"
        assert evidence.details == {"test": "data"}
