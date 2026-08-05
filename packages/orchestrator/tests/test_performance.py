"""
Performance Tests for Orchestrator

This module contains performance tests for the orchestrator components,
measuring execution time and resource usage.
"""

import pytest
import time
from typing import List

from src.orchestrator.bayesian_engine import (
    BayesianEngine,
    AgentResult,
    AgentStatus,
)
from src.orchestrator.verdict import VerdictGenerator
from src.orchestrator.recommendation import RecommendationEngine


class TestBayesianEnginePerformance:
    """Performance tests for Bayesian Engine"""

    def test_calculate_trust_score_performance(self):
        """Test trust score calculation performance"""
        engine = BayesianEngine()

        # Create 100 agent results
        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(100)
        ]

        start_time = time.time()
        trust_score, metadata = engine.calculate_trust_score(results)
        elapsed = time.time() - start_time

        assert elapsed < 1.0  # Should complete in under 1 second
        assert 0.0 <= trust_score <= 1.0

    def test_calculate_beta_posterior_performance(self):
        """Test Beta posterior calculation performance"""
        engine = BayesianEngine()

        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(100)
        ]

        start_time = time.time()
        alpha, beta, expected = engine.calculate_beta_posterior(results)
        elapsed = time.time() - start_time

        assert elapsed < 0.5  # Should complete in under 0.5 seconds
        assert alpha > 0
        assert beta > 0

    def test_detect_anomaly_performance(self):
        """Test anomaly detection performance"""
        engine = BayesianEngine()

        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(100)
        ]

        start_time = time.time()
        anomaly = engine.detect_anomaly(results, 0.5)
        elapsed = time.time() - start_time

        assert elapsed < 0.1  # Should complete in under 0.1 seconds

    def test_analyze_trend_performance(self):
        """Test trend analysis performance"""
        engine = BayesianEngine()

        history = [0.5 + (i % 20) * 0.02 for i in range(1000)]

        start_time = time.time()
        trend = engine.analyze_trend(history)
        elapsed = time.time() - start_time

        assert elapsed < 0.1  # Should complete in under 0.1 seconds
        assert "trend" in trend


class TestVerdictGeneratorPerformance:
    """Performance tests for Verdict Generator"""

    def test_generate_verdict_performance(self):
        """Test verdict generation performance"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)

        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(50)
        ]

        start_time = time.time()
        verdict = verdict_gen.generate_verdict(results)
        elapsed = time.time() - start_time

        assert elapsed < 1.0  # Should complete in under 1 second
        assert verdict.trust_score >= 0.0
        assert verdict.trust_score <= 1.0

    def test_generate_verdict_with_history_performance(self):
        """Test verdict generation with history performance"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)

        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(50)
        ]

        history = [0.5 + (i % 20) * 0.02 for i in range(100)]

        start_time = time.time()
        verdict = verdict_gen.generate_verdict(results, history)
        elapsed = time.time() - start_time

        assert elapsed < 1.0  # Should complete in under 1 second
        assert verdict.trend is not None


class TestRecommendationEnginePerformance:
    """Performance tests for Recommendation Engine"""

    def test_generate_recommendations_performance(self):
        """Test recommendation generation performance"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)
        rec_engine = RecommendationEngine()

        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(50)
        ]

        verdict = verdict_gen.generate_verdict(results)

        start_time = time.time()
        report = rec_engine.generate_recommendations(verdict)
        elapsed = time.time() - start_time

        assert elapsed < 1.0  # Should complete in under 1 second
        assert len(report.recommendations) > 0

    def test_get_priority_recommendations_performance(self):
        """Test priority filtering performance"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)
        rec_engine = RecommendationEngine()

        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.2 if i < 10 else 0.8,
                confidence=0.8,
                data={},
                metadata={},
            )
            for i in range(50)
        ]

        verdict = verdict_gen.generate_verdict(results)
        report = rec_engine.generate_recommendations(verdict)

        from src.orchestrator.recommendation import RecommendationPriority

        start_time = time.time()
        filtered = rec_engine.get_priority_recommendations(report, RecommendationPriority.HIGH)
        elapsed = time.time() - start_time

        assert elapsed < 0.1  # Should complete in under 0.1 seconds


class TestMemoryUsage:
    """Memory usage tests"""

    def test_large_agent_results_memory(self):
        """Test memory usage with large number of agent results"""
        import sys

        engine = BayesianEngine()

        # Create 1000 agent results
        results = [
            AgentResult(
                agent_id=f"agent_{i}",
                status=AgentStatus.COMPLETED,
                score=0.5 + (i % 10) * 0.05,
                confidence=0.8,
                data={"key": f"value_{i}"},
                metadata={"execution_time": i},
            )
            for i in range(1000)
        ]

        # Calculate memory usage
        size = sys.getsizeof(results)
        assert size < 100 * 1024 * 1024  # Should be under 100MB

        # Test processing
        trust_score, metadata = engine.calculate_trust_score(results)
        assert 0.0 <= trust_score <= 1.0


class TestConcurrentPerformance:
    """Concurrent operation performance tests"""

    def test_multiple_verdict_generation(self):
        """Test generating multiple verdicts in sequence"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)

        results = [
            AgentResult(
                agent_id="chronos",
                status=AgentStatus.COMPLETED,
                score=0.85,
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

        start_time = time.time()
        for _ in range(100):
            verdict = verdict_gen.generate_verdict(results)
        elapsed = time.time() - start_time

        avg_time = elapsed / 100
        assert avg_time < 0.01  # Average should be under 10ms


class TestScalability:
    """Scalability tests"""

    def test_scalability_with_agent_count(self):
        """Test scalability with increasing agent count"""
        engine = BayesianEngine()
        verdict_gen = VerdictGenerator(engine)

        agent_counts = [4, 10, 50, 100]
        times = []

        for count in agent_counts:
            results = [
                AgentResult(
                    agent_id=f"agent_{i}",
                    status=AgentStatus.COMPLETED,
                    score=0.5 + (i % 10) * 0.05,
                    confidence=0.8,
                    data={},
                    metadata={},
                )
                for i in range(count)
            ]

            start_time = time.time()
            verdict = verdict_gen.generate_verdict(results)
            elapsed = time.time() - start_time
            times.append(elapsed)

        # Time should scale roughly linearly or better
        # 100 agents should not take more than 10x the time of 10 agents
        assert times[3] < times[1] * 10

    def test_scalability_with_history_size(self):
        """Test scalability with increasing history size"""
        engine = BayesianEngine()

        history_sizes = [10, 50, 100, 500]
        times = []

        for size in history_sizes:
            history = [0.5 + (i % 20) * 0.02 for i in range(size)]

            start_time = time.time()
            trend = engine.analyze_trend(history)
            elapsed = time.time() - start_time
            times.append(elapsed)

        # Trend analysis should be efficient even with large history
        assert max(times) < 0.5  # All should complete in under 0.5 seconds
