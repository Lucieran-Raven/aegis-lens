"""
Verdict Generation Module

This module implements the final verdict generation system that combines
trust scores, agent results, and anomaly detection to produce detailed
authenticity verdicts with explanations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import logging

from .bayesian_engine import (
    BayesianEngine,
    AgentResult,
    AgentStatus,
)


class VerdictStatus(Enum):
    """Final verdict status"""

    CLEAR = "CLEAR"
    SUSPECT = "SUSPECT"
    LIKELY_FAKE = "LIKELY_FAKE"
    FAKE = "FAKE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class VerdictEvidence:
    """Evidence supporting the verdict"""

    agent_id: str
    score: float
    confidence: float
    weight: float
    contribution: str  # "positive", "negative", or "neutral"
    details: Dict[str, Any]


@dataclass
class Verdict:
    """Final authenticity verdict"""

    status: VerdictStatus
    trust_score: float
    confidence: float  # Overall confidence in the verdict
    evidence: List[VerdictEvidence]
    reasoning: str
    anomaly: Optional[Dict] = None
    trend: Optional[Dict] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class VerdictGenerator:
    """
    Verdict Generator for producing detailed authenticity verdicts.

    Combines Bayesian engine results with evidence aggregation and
    anomaly detection to produce comprehensive verdicts with explanations.
    """

    def __init__(self, bayesian_engine: Optional[BayesianEngine] = None):
        """
        Initialize Verdict Generator.

        Args:
            bayesian_engine: Bayesian engine instance (creates default if None)
        """
        self.bayesian_engine = bayesian_engine or BayesianEngine()
        self.logger = logging.getLogger(__name__)

    def generate_verdict(
        self,
        results: List[AgentResult],
        history: Optional[List[float]] = None,
    ) -> Verdict:
        """
        Generate a comprehensive authenticity verdict.

        Args:
            results: List of agent results
            history: Optional historical trust scores for trend analysis

        Returns:
            Verdict object with status, evidence, and reasoning
        """
        # Calculate trust score using Bayesian engine
        trust_score, metadata = self.bayesian_engine.calculate_trust_score(results)

        # Detect anomalies
        anomaly = self.bayesian_engine.detect_anomaly(results, trust_score)

        # Analyze trend if history provided
        trend = None
        if history:
            trend = self.bayesian_engine.analyze_trend(history)

        # Determine status
        completed_count = len([r for r in results if r.status == AgentStatus.COMPLETED])
        status = self._determine_status(trust_score, anomaly, trend, completed_count)

        # Calculate overall confidence
        confidence = self._calculate_confidence(results, metadata, anomaly)

        # Aggregate evidence
        evidence = self._aggregate_evidence(results, metadata)

        # Generate reasoning
        reasoning = self._generate_reasoning(trust_score, status, evidence, anomaly, trend)

        # Build verdict
        verdict = Verdict(
            status=status,
            trust_score=trust_score,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            anomaly=anomaly,
            trend=trend,
            metadata=metadata,
        )

        self.logger.info(
            f"Generated verdict: {status.value} (trust={trust_score:.2f}, conf={confidence:.2f})"
        )

        return verdict

    def _determine_status(
        self,
        trust_score: float,
        anomaly: Optional[Dict],
        trend: Optional[Dict],
        completed_count: int = 0,
    ) -> VerdictStatus:
        """
        Determine verdict status based on trust score and context.

        Args:
            trust_score: Calculated trust score
            anomaly: Anomaly detection result
            trend: Trend analysis result
            completed_count: Number of completed agents

        Returns:
            VerdictStatus enum value
        """
        # Check for inconclusive cases
        if completed_count < 2:
            return VerdictStatus.INCONCLUSIVE

        # High severity anomaly overrides trust score
        if anomaly and anomaly.get("severity") == "HIGH":
            if trust_score > 0.5:
                return VerdictStatus.SUSPECT
            return VerdictStatus.LIKELY_FAKE

        # Declining trend with moderate trust score
        if trend and trend.get("trend") == "DECLINING" and 0.5 <= trust_score < 0.7:
            return VerdictStatus.SUSPECT

        # Standard trust score thresholds
        if trust_score >= 0.8:
            return VerdictStatus.CLEAR
        elif trust_score >= 0.5:
            return VerdictStatus.SUSPECT
        elif trust_score >= 0.3:
            return VerdictStatus.LIKELY_FAKE
        else:
            return VerdictStatus.FAKE

    def _calculate_confidence(
        self,
        results: List[AgentResult],
        metadata: Dict,
        anomaly: Optional[Dict],
    ) -> float:
        """
        Calculate overall confidence in the verdict.

        Args:
            results: Agent results
            metadata: Bayesian engine metadata
            anomaly: Anomaly detection result

        Returns:
            Confidence score (0-1)
        """
        completed_count = metadata.get("agent_count", 0)

        # Base confidence from number of agents
        if completed_count >= 4:
            base_confidence = 0.9
        elif completed_count >= 3:
            base_confidence = 0.8
        elif completed_count >= 2:
            base_confidence = 0.7
        else:
            base_confidence = 0.5

        # Reduce confidence if anomaly detected
        if anomaly:
            if anomaly.get("severity") == "HIGH":
                base_confidence -= 0.2
            else:
                base_confidence -= 0.1

        # Adjust based on credibility interval width
        credibility_interval = metadata.get("credibility_interval", (0, 1))
        interval_width = credibility_interval[1] - credibility_interval[0]
        if interval_width > 0.4:
            base_confidence -= 0.15
        elif interval_width > 0.3:
            base_confidence -= 0.1

        # Ensure confidence is in valid range
        return max(0.3, min(0.95, base_confidence))

    def _aggregate_evidence(
        self,
        results: List[AgentResult],
        metadata: Dict,
    ) -> List[VerdictEvidence]:
        """
        Aggregate evidence from all agents.

        Args:
            results: Agent results
            metadata: Bayesian engine metadata

        Returns:
            List of VerdictEvidence objects
        """
        evidence_list = []
        contributions = metadata.get("contributions", {})

        for result in results:
            if result.status != AgentStatus.COMPLETED:
                continue

            weight = self.bayesian_engine._get_agent_weight(result.agent_id)
            contribution = contributions.get(result.agent_id, 0)

            # Determine contribution type
            if result.score >= 0.7:
                contrib_type = "positive"
            elif result.score <= 0.3:
                contrib_type = "negative"
            else:
                contrib_type = "neutral"

            evidence = VerdictEvidence(
                agent_id=result.agent_id,
                score=result.score,
                confidence=result.confidence,
                weight=weight,
                contribution=contrib_type,
                details=result.data,
            )
            evidence_list.append(evidence)

        # Sort by contribution (positive first, then neutral, then negative)
        evidence_list.sort(key=lambda e: e.score, reverse=True)

        return evidence_list

    def _generate_reasoning(
        self,
        trust_score: float,
        status: VerdictStatus,
        evidence: List[VerdictEvidence],
        anomaly: Optional[Dict],
        trend: Optional[Dict],
    ) -> str:
        """
        Generate human-readable reasoning for the verdict.

        Args:
            trust_score: Trust score
            status: Verdict status
            evidence: Evidence list
            anomaly: Anomaly detection result
            trend: Trend analysis result

        Returns:
            Reasoning string
        """
        reasoning_parts = []

        # Start with trust score explanation
        reasoning_parts.append(
            f"Trust score of {trust_score:.2f} indicates {status.value.lower()} authenticity."
        )

        # Add evidence summary
        positive_count = sum(1 for e in evidence if e.contribution == "positive")
        negative_count = sum(1 for e in evidence if e.contribution == "negative")
        neutral_count = sum(1 for e in evidence if e.contribution == "neutral")

        if positive_count > 0:
            reasoning_parts.append(
                f"{positive_count} agent(s) provided positive evidence of authenticity."
            )
        if negative_count > 0:
            reasoning_parts.append(f"{negative_count} agent(s) indicated potential manipulation.")
        if neutral_count > 0:
            reasoning_parts.append(f"{neutral_count} agent(s) provided neutral results.")

        # Add anomaly information
        if anomaly:
            if anomaly["type"] == "HIGH_VARIANCE":
                reasoning_parts.append(
                    f"High variance ({anomaly['std_score']:.2f}) detected among agent results, "
                    "indicating significant disagreement."
                )
            elif anomaly["type"] == "OUTLIER_AGENT":
                reasoning_parts.append(
                    f"Agent {anomaly['agent_id']} is an outlier with z-score of "
                    f"{anomaly['z_score']:.2f}, suggesting potential issue."
                )

        # Add trend information
        if trend and trend["trend"] != "INSUFFICIENT_DATA":
            reasoning_parts.append(
                f"Trend analysis shows {trend['trend'].lower()} pattern "
                f"(slope: {trend['slope']:.3f})."
            )

        # Combine all parts
        return " ".join(reasoning_parts)

    def generate_summary(self, verdict: Verdict) -> Dict[str, Any]:
        """
        Generate a summary of the verdict for API responses.

        Args:
            verdict: Verdict object

        Returns:
            Summary dictionary
        """
        return {
            "status": verdict.status.value,
            "trust_score": verdict.trust_score,
            "confidence": verdict.confidence,
            "reasoning": verdict.reasoning,
            "evidence_count": len(verdict.evidence),
            "has_anomaly": verdict.anomaly is not None,
            "has_trend": verdict.trend is not None,
            "generated_at": verdict.generated_at.isoformat(),
        }
