"""
Bayesian Engine for Probabilistic Agent Fusion

This module implements Bayesian inference to fuse results from multiple AI agents,
calculating trust scores and generating final verdicts.
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging


class AgentStatus(Enum):
    """Agent status enum matching base agent status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentResult:
    """Result from an AI agent"""

    agent_id: str
    status: AgentStatus
    score: float  # 0-1 confidence score
    confidence: float  # 0-1 confidence in the result
    data: Dict  # Additional agent-specific data
    metadata: Dict  # Execution metadata


@dataclass
class PriorParameters:
    """Prior parameters for Bayesian inference"""

    alpha: float  # Prior strength for positive evidence
    beta: float  # Prior strength for negative evidence
    base_reliability: float  # Base reliability score (0-1)


@dataclass
class AgentWeights:
    """Dynamic weights for each agent"""

    chronos: float = 0.25  # Hardware integrity
    echo: float = 0.20  # Audio integrity
    iris: float = 0.25  # Visual liveness
    lipsync: float = 0.20  # Media integrity
    nova: float = 0.10  # Behavioral linguistics


class BayesianEngine:
    """
    Bayesian Engine for probabilistic agent result fusion.

    Uses Beta-Binomial conjugate prior model for updating beliefs
    about candidate authenticity based on agent results.
    """

    def __init__(self, priors: Optional[PriorParameters] = None):
        """
        Initialize Bayesian Engine.

        Args:
            priors: Prior parameters for inference
        """
        self.priors = priors or PriorParameters(
            alpha=2.0,  # Weak prior favoring authenticity
            beta=1.0,
            base_reliability=0.7,
        )
        self.weights = AgentWeights()
        self.logger = logging.getLogger(__name__)

    def update_priors(self, alpha: float, beta: float, base_reliability: float) -> None:
        """
        Update prior parameters.

        Args:
            alpha: Prior strength for positive evidence
            beta: Prior strength for negative evidence
            base_reliability: Base reliability score
        """
        self.priors = PriorParameters(alpha, beta, base_reliability)
        self.logger.info(f"Updated priors: alpha={alpha}, beta={beta}")

    def set_agent_weights(self, weights: AgentWeights) -> None:
        """
        Set agent weights for fusion.

        Args:
            weights: Agent weight configuration
        """
        self.weights = weights
        self.logger.info(f"Updated agent weights: {weights}")

    def calculate_weighted_score(
        self, results: List[AgentResult]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate weighted average of agent scores.

        Args:
            results: List of agent results

        Returns:
            Tuple of (weighted_score, individual_contributions)
        """
        if not results:
            return 0.5, {}

        contributions = {}
        weighted_sum = 0.0
        total_weight = 0.0

        for result in results:
            if result.status != AgentStatus.COMPLETED:
                continue

            weight = self._get_agent_weight(result.agent_id)
            contribution = result.score * weight * result.confidence
            contributions[result.agent_id] = contribution

            weighted_sum += contribution
            total_weight += weight * result.confidence

        if total_weight == 0:
            return 0.5, contributions

        weighted_score = weighted_sum / total_weight
        return weighted_score, contributions

    def _get_agent_weight(self, agent_id: str) -> float:
        """
        Get weight for a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Weight value
        """
        agent_map = {
            "chronos": self.weights.chronos,
            "echo": self.weights.echo,
            "iris": self.weights.iris,
            "lipsync": self.weights.lipsync,
            "nova": self.weights.nova,
        }
        return agent_map.get(agent_id.lower(), 0.1)

    def calculate_beta_posterior(self, results: List[AgentResult]) -> Tuple[float, float, float]:
        """
        Calculate Beta posterior distribution parameters.

        Uses agent scores as evidence for/against authenticity.

        Args:
            results: List of agent results

        Returns:
            Tuple of (alpha_post, beta_post, expected_value)
        """
        alpha_post = self.priors.alpha
        beta_post = self.priors.beta

        for result in results:
            if result.status != AgentStatus.COMPLETED:
                continue

            weight = self._get_agent_weight(result.agent_id)

            # Update based on agent score
            if result.score >= 0.7:
                # Strong evidence for authenticity
                alpha_post += result.score * weight * 2
            elif result.score <= 0.3:
                # Strong evidence against authenticity
                beta_post += (1.0 - result.score) * weight * 2
            else:
                # Weak evidence
                alpha_post += result.score * weight
                beta_post += (1.0 - result.score) * weight

        expected_value = alpha_post / (alpha_post + beta_post)
        return alpha_post, beta_post, expected_value

    def calculate_credibility_interval(
        self, alpha: float, beta: float, confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate Bayesian credibility interval.

        Args:
            alpha: Beta distribution alpha parameter
            beta: Beta distribution beta parameter
            confidence: Confidence level (0-1)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        lower = stats.beta.ppf((1 - confidence) / 2, alpha, beta)
        upper = stats.beta.ppf(1 - (1 - confidence) / 2, alpha, beta)
        return lower, upper

    def calculate_trust_score(self, results: List[AgentResult]) -> Tuple[float, Dict]:
        """
        Calculate overall trust score using Bayesian fusion.

        Combines weighted scoring with Bayesian posterior inference.

        Args:
            results: List of agent results

        Returns:
            Tuple of (trust_score, metadata)
        """
        # Calculate weighted score
        weighted_score, contributions = self.calculate_weighted_score(results)

        # Calculate Bayesian posterior
        alpha_post, beta_post, expected_value = self.calculate_beta_posterior(results)

        # Calculate credibility interval
        lower, upper = self.calculate_credibility_interval(alpha_post, beta_post)

        # Fuse weighted and Bayesian scores
        # Weighted score represents current evidence
        # Expected value represents posterior belief
        trust_score = 0.6 * weighted_score + 0.4 * expected_value

        # Apply base reliability adjustment
        trust_score = trust_score * (0.5 + 0.5 * self.priors.base_reliability)

        metadata = {
            "weighted_score": weighted_score,
            "bayesian_expected": expected_value,
            "alpha_posterior": alpha_post,
            "beta_posterior": beta_post,
            "credibility_interval": (lower, upper),
            "contributions": contributions,
            "agent_count": len([r for r in results if r.status == AgentStatus.COMPLETED]),
        }

        return trust_score, metadata

    def determine_status(self, trust_score: float) -> str:
        """
        Determine status based on trust score.

        Args:
            trust_score: Trust score (0-1)

        Returns:
            Status string
        """
        if trust_score >= 0.8:
            return "CLEAR"
        elif trust_score >= 0.5:
            return "SUSPECT"
        elif trust_score >= 0.3:
            return "LIKELY_FAKE"
        else:
            return "FAKE"

    def detect_anomaly(self, results: List[AgentResult], trust_score: float) -> Optional[Dict]:
        """
        Detect anomalies in agent results.

        Args:
            results: List of agent results
            trust_score: Overall trust score

        Returns:
            Anomaly detection result or None
        """
        completed_results = [r for r in results if r.status == AgentStatus.COMPLETED]

        if len(completed_results) < 2:
            return None

        scores = [r.score for r in completed_results]
        mean_score = np.mean(scores)
        std_score = np.std(scores)

        # Check for high variance (agents disagree)
        if std_score > 0.3:
            return {
                "type": "HIGH_VARIANCE",
                "severity": "HIGH" if std_score > 0.5 else "MEDIUM",
                "mean_score": mean_score,
                "std_score": std_score,
                "description": "Agents show significant disagreement",
            }

        # Check for outlier agents
        for result in completed_results:
            z_score = abs((result.score - mean_score) / (std_score + 1e-10))
            if z_score > 2.0:
                return {
                    "type": "OUTLIER_AGENT",
                    "severity": "MEDIUM",
                    "agent_id": result.agent_id,
                    "score": result.score,
                    "z_score": z_score,
                    "description": f"Agent {result.agent_id} is an outlier",
                }

        return None

    def analyze_trend(self, history: List[float], window_size: int = 10) -> Dict[str, float]:
        """
        Analyze trend in trust scores over time.

        Args:
            history: List of historical trust scores
            window_size: Size of moving average window

        Returns:
            Trend analysis metrics
        """
        if len(history) < 2:
            return {"trend": "INSUFFICIENT_DATA", "slope": 0.0}

        recent = history[-window_size:] if len(history) >= window_size else history

        # Calculate linear regression slope
        x = np.arange(len(recent))
        y = np.array(recent)
        slope, _ = np.polyfit(x, y, 1)

        # Determine trend direction
        if slope > 0.01:
            trend = "IMPROVING"
        elif slope < -0.01:
            trend = "DECLINING"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "slope": slope,
            "current": history[-1],
            "average": np.mean(recent),
            "min": np.min(recent),
            "max": np.max(recent),
        }
