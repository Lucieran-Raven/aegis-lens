"""
Recommendation Engine Module

This module implements the recommendation system that analyzes verdicts
and provides actionable recommendations for HR managers and interviewers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

from .verdict import Verdict, VerdictStatus


class RecommendationType(Enum):
    """Type of recommendation"""

    QUESTION = "question"  # Suggested follow-up question
    FLAG = "flag"  # Flag for attention
    ACTION = "action"  # Recommended action
    INSIGHT = "insight"  # Analytical insight


class RecommendationPriority(Enum):
    """Priority level of recommendation"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """A single recommendation"""

    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_questions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationReport:
    """Complete recommendation report"""

    verdict_status: VerdictStatus
    trust_score: float
    recommendations: List[Recommendation]
    summary: str
    risk_level: str
    suggested_interview_flow: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecommendationEngine:
    """
    Recommendation Engine for generating actionable insights.

    Analyzes verdicts and provides recommendations for interviewers
    including suggested questions, flags, and actions.
    """

    def __init__(self):
        """Initialize Recommendation Engine"""
        self.logger = logging.getLogger(__name__)

    def generate_recommendations(self, verdict: Verdict) -> RecommendationReport:
        """
        Generate comprehensive recommendations based on verdict.

        Args:
            verdict: Verdict object from the verdict generator

        Returns:
            RecommendationReport with all recommendations
        """
        recommendations = []

        # Generate recommendations based on verdict status
        if verdict.status == VerdictStatus.FAKE:
            recommendations.extend(self._generate_fake_recommendations(verdict))
        elif verdict.status == VerdictStatus.LIKELY_FAKE:
            recommendations.extend(self._generate_likely_fake_recommendations(verdict))
        elif verdict.status == VerdictStatus.SUSPECT:
            recommendations.extend(self._generate_suspect_recommendations(verdict))
        elif verdict.status == VerdictStatus.CLEAR:
            recommendations.extend(self._generate_clear_recommendations(verdict))
        else:
            recommendations.extend(self._generate_inconclusive_recommendations(verdict))

        # Add anomaly-based recommendations
        if verdict.anomaly:
            recommendations.extend(self._generate_anomaly_recommendations(verdict))

        # Add trend-based recommendations
        if verdict.trend:
            recommendations.extend(self._generate_trend_recommendations(verdict))

        # Add evidence-based recommendations
        recommendations.extend(self._generate_evidence_recommendations(verdict))

        # Determine risk level
        risk_level = self._determine_risk_level(verdict)

        # Generate summary
        summary = self._generate_summary(verdict, recommendations, risk_level)

        # Generate suggested interview flow
        interview_flow = self._generate_interview_flow(verdict, recommendations)

        report = RecommendationReport(
            verdict_status=verdict.status,
            trust_score=verdict.trust_score,
            recommendations=recommendations,
            summary=summary,
            risk_level=risk_level,
            suggested_interview_flow=interview_flow,
            metadata={
                "verdict_confidence": verdict.confidence,
                "evidence_count": len(verdict.evidence),
                "has_anomaly": verdict.anomaly is not None,
                "has_trend": verdict.trend is not None,
            },
        )

        self.logger.info(
            f"Generated {len(recommendations)} recommendations for {verdict.status.value}"
        )

        return report

    def _generate_fake_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations for FAKE verdict"""
        recommendations = []

        # Critical flag
        recommendations.append(
            Recommendation(
                type=RecommendationType.FLAG,
                priority=RecommendationPriority.CRITICAL,
                title="High Risk of Manipulation Detected",
                description="Multiple indicators suggest the candidate may be using unauthorized tools or manipulation techniques.",
                context={"trust_score": verdict.trust_score},
                suggested_questions=[
                    "Can you explain any technical issues you experienced during the interview?",
                    "Are you using any assistive technologies or tools?",
                ],
            )
        )

        # Action recommendation
        recommendations.append(
            Recommendation(
                type=RecommendationType.ACTION,
                priority=RecommendationPriority.CRITICAL,
                title="Terminate or Escalate",
                description="Consider terminating the interview or escalating to a senior interviewer for manual review.",
                context={},
                suggested_questions=[],
            )
        )

        return recommendations

    def _generate_likely_fake_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations for LIKELY_FAKE verdict"""
        recommendations = []

        # High priority flag
        recommendations.append(
            Recommendation(
                type=RecommendationType.FLAG,
                priority=RecommendationPriority.HIGH,
                title="Suspicious Activity Detected",
                description="Several indicators suggest potential manipulation or unauthorized tool usage.",
                context={"trust_score": verdict.trust_score},
                suggested_questions=[
                    "I noticed some inconsistencies in your responses. Can you clarify?",
                    "Are you familiar with the technical requirements of this interview?",
                ],
            )
        )

        # Question recommendations
        recommendations.append(
            Recommendation(
                type=RecommendationType.QUESTION,
                priority=RecommendationPriority.HIGH,
                title="Deep Technical Verification",
                description="Ask technical questions that require real-time problem solving.",
                context={},
                suggested_questions=[
                    "Can you walk me through your thought process for this problem?",
                    "How would you approach this differently if constraints changed?",
                ],
            )
        )

        return recommendations

    def _generate_suspect_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations for SUSPECT verdict"""
        recommendations = []

        # Medium priority flag
        recommendations.append(
            Recommendation(
                type=RecommendationType.FLAG,
                priority=RecommendationPriority.MEDIUM,
                title="Moderate Concern Detected",
                description="Some indicators suggest potential issues, but evidence is not conclusive.",
                context={"trust_score": verdict.trust_score},
                suggested_questions=[
                    "Can you elaborate on your previous answer?",
                    "What would you do if you encountered this scenario in production?",
                ],
            )
        )

        # Insight recommendation
        recommendations.append(
            Recommendation(
                type=RecommendationType.INSIGHT,
                priority=RecommendationPriority.MEDIUM,
                title="Monitor Closely",
                description="Continue monitoring for additional indicators. Current evidence is inconclusive.",
                context={},
                suggested_questions=[],
            )
        )

        return recommendations

    def _generate_clear_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations for CLEAR verdict"""
        recommendations = []

        # Low priority insight
        recommendations.append(
            Recommendation(
                type=RecommendationType.INSIGHT,
                priority=RecommendationPriority.LOW,
                title="No Manipulation Detected",
                description="All indicators suggest authentic behavior. Proceed with standard interview.",
                context={"trust_score": verdict.trust_score},
                suggested_questions=[],
            )
        )

        return recommendations

    def _generate_inconclusive_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations for INCONCLUSIVE verdict"""
        recommendations = []

        # Medium priority flag
        recommendations.append(
            Recommendation(
                type=RecommendationType.FLAG,
                priority=RecommendationPriority.MEDIUM,
                title="Insufficient Data",
                description="Not enough agent data to make a determination. Continue interview.",
                context={"agent_count": len(verdict.evidence)},
                suggested_questions=[],
            )
        )

        # Action recommendation
        recommendations.append(
            Recommendation(
                type=RecommendationType.ACTION,
                priority=RecommendationPriority.MEDIUM,
                title="Continue Data Collection",
                description="Allow more time for agents to collect data before making a determination.",
                context={},
                suggested_questions=[],
            )
        )

        return recommendations

    def _generate_anomaly_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations based on anomalies"""
        recommendations = []

        if not verdict.anomaly:
            return recommendations

        anomaly_type = verdict.anomaly.get("type")

        if anomaly_type == "HIGH_VARIANCE":
            recommendations.append(
                Recommendation(
                    type=RecommendationType.INSIGHT,
                    priority=RecommendationPriority.HIGH,
                    title="Agent Disagreement Detected",
                    description="Agents show significant disagreement in their assessments.",
                    context=verdict.anomaly,
                    suggested_questions=[
                        "Can you provide more context for your answers?",
                        "Would you like to clarify any of your previous responses?",
                    ],
                )
            )
        elif anomaly_type == "OUTLIER_AGENT":
            recommendations.append(
                Recommendation(
                    type=RecommendationType.INSIGHT,
                    priority=RecommendationPriority.MEDIUM,
                    title="Anomalous Agent Result",
                    description=f"Agent {verdict.anomaly.get('agent_id')} produced an outlier result.",
                    context=verdict.anomaly,
                    suggested_questions=[],
                )
            )

        return recommendations

    def _generate_trend_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations based on trends"""
        recommendations = []

        if not verdict.trend:
            return recommendations

        trend = verdict.trend.get("trend")

        if trend == "DECLINING":
            recommendations.append(
                Recommendation(
                    type=RecommendationType.FLAG,
                    priority=RecommendationPriority.HIGH,
                    title="Declining Trust Trend",
                    description="Trust score has been declining over recent measurements.",
                    context=verdict.trend,
                    suggested_questions=[
                        "Have you experienced any technical difficulties recently?",
                        "Is there anything affecting your performance?",
                    ],
                )
            )
        elif trend == "IMPROVING":
            recommendations.append(
                Recommendation(
                    type=RecommendationType.INSIGHT,
                    priority=RecommendationPriority.LOW,
                    title="Improving Trust Trend",
                    description="Trust score has been improving over recent measurements.",
                    context=verdict.trend,
                    suggested_questions=[],
                )
            )

        return recommendations

    def _generate_evidence_recommendations(self, verdict: Verdict) -> List[Recommendation]:
        """Generate recommendations based on evidence"""
        recommendations = []

        # Check for negative evidence
        negative_evidence = [e for e in verdict.evidence if e.contribution == "negative"]

        if negative_evidence:
            for evidence in negative_evidence:
                recommendations.append(
                    Recommendation(
                        type=RecommendationType.QUESTION,
                        priority=RecommendationPriority.HIGH,
                        title=f"Concern from {evidence.agent_id.upper()} Agent",
                        description=f"{evidence.agent_id} agent detected potential issues.",
                        context={
                            "agent_id": evidence.agent_id,
                            "score": evidence.score,
                            "details": evidence.details,
                        },
                        suggested_questions=self._get_agent_specific_questions(evidence.agent_id),
                    )
                )

        return recommendations

    def _get_agent_specific_questions(self, agent_id: str) -> List[str]:
        """Get agent-specific follow-up questions"""
        question_map = {
            "chronos": [
                "Have you experienced any frame rate issues or lag?",
                "Are you using any virtualization or remote desktop tools?",
            ],
            "echo": [
                "Can you hear me clearly?",
                "Are you using any audio enhancement tools?",
            ],
            "iris": [
                "Can you look directly at the camera?",
                "Are you in a well-lit environment?",
            ],
            "lipsync": [
                "Can you speak more slowly?",
                "Is your microphone working properly?",
            ],
        }
        return question_map.get(agent_id.lower(), [])

    def _determine_risk_level(self, verdict: Verdict) -> str:
        """Determine overall risk level"""
        if verdict.status in [VerdictStatus.FAKE, VerdictStatus.LIKELY_FAKE]:
            return "HIGH"
        elif verdict.status == VerdictStatus.SUSPECT:
            return "MEDIUM"
        elif verdict.status == VerdictStatus.INCONCLUSIVE:
            return "UNKNOWN"
        else:
            return "LOW"

    def _generate_summary(
        self, verdict: Verdict, recommendations: List[Recommendation], risk_level: str
    ) -> str:
        """Generate summary of recommendations"""
        critical_count = sum(
            1 for r in recommendations if r.priority == RecommendationPriority.CRITICAL
        )
        high_count = sum(1 for r in recommendations if r.priority == RecommendationPriority.HIGH)

        summary_parts = [
            f"Verdict status is {verdict.status.value} with trust score of {verdict.trust_score:.2f}.",
            f"Overall risk level: {risk_level}.",
        ]

        if critical_count > 0:
            summary_parts.append(
                f"{critical_count} critical recommendation(s) require immediate attention."
            )
        if high_count > 0:
            summary_parts.append(
                f"{high_count} high priority recommendation(s) should be reviewed."
            )

        return " ".join(summary_parts)

    def _generate_interview_flow(
        self, verdict: Verdict, recommendations: List[Recommendation]
    ) -> List[str]:
        """Generate suggested interview flow"""
        flow = []

        if verdict.status in [VerdictStatus.FAKE, VerdictStatus.LIKELY_FAKE]:
            flow = [
                "Pause interview",
                "Review critical flags",
                "Consider escalation",
                "If continuing: ask deep technical questions",
                "Monitor for additional indicators",
            ]
        elif verdict.status == VerdictStatus.SUSPECT:
            flow = [
                "Continue interview with caution",
                "Ask follow-up questions on concerning areas",
                "Monitor for additional indicators",
                "Reassess after more data collected",
            ]
        elif verdict.status == VerdictStatus.CLEAR:
            flow = [
                "Continue standard interview flow",
                "No special actions required",
            ]
        else:  # INCONCLUSIVE
            flow = [
                "Continue interview",
                "Allow more time for data collection",
                "Reassess when more data available",
            ]

        return flow

    def get_priority_recommendations(
        self, report: RecommendationReport, min_priority: RecommendationPriority
    ) -> List[Recommendation]:
        """
        Filter recommendations by minimum priority.

        Args:
            report: Recommendation report
            min_priority: Minimum priority level to include

        Returns:
            Filtered list of recommendations
        """
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3,
        }

        min_level = priority_order[min_priority]
        filtered = [r for r in report.recommendations if priority_order[r.priority] <= min_level]

        # Sort by priority
        filtered.sort(key=lambda r: priority_order[r.priority])

        return filtered
