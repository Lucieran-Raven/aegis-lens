"""
FastAPI Service for Orchestrator

This module provides the REST API for the Bayesian Orchestrator,
exposing endpoints for verdict generation and recommendations.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging
import traceback

from src.orchestrator.bayesian_engine import (
    BayesianEngine,
    AgentResult,
    AgentStatus,
    PriorParameters,
    AgentWeights,
)
from src.orchestrator.verdict import VerdictGenerator, Verdict
from src.orchestrator.recommendation import RecommendationEngine, RecommendationReport


class OrchestratorError(Exception):
    """Base exception for orchestrator errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(OrchestratorError):
    """Validation error"""

    pass


class ProcessingError(OrchestratorError):
    """Processing error"""

    pass


# Pydantic models for requests/responses
class AgentResultRequest(BaseModel):
    """Request model for agent result"""

    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="Agent status")
    score: float = Field(..., ge=0.0, le=1.0, description="Agent confidence score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in result")
    data: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate agent status"""
        valid_statuses = ["pending", "running", "completed", "error"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Invalid status: {v}. Must be one of {valid_statuses}")
        return v.lower()

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, v: str) -> str:
        """Validate agent ID"""
        if not v or not isinstance(v, str):
            raise ValueError("Agent ID must be a non-empty string")
        valid_agents = ["chronos", "echo", "iris", "lipsync", "nova"]
        if v.lower() not in valid_agents:
            raise ValueError(f"Unknown agent: {v}. Must be one of {valid_agents}")
        return v.lower()


class VerdictRequest(BaseModel):
    """Request model for verdict generation"""

    agent_results: List[AgentResultRequest] = Field(
        ..., description="List of agent results"
    )
    history: Optional[List[float]] = Field(
        None, description="Historical trust scores for trend analysis"
    )
    priors: Optional[PriorParameters] = Field(
        None, description="Optional prior parameters for Bayesian engine"
    )
    weights: Optional[AgentWeights] = Field(
        None, description="Optional agent weights for fusion"
    )


class VerdictResponse(BaseModel):
    """Response model for verdict"""

    status: str
    trust_score: float
    confidence: float
    reasoning: str
    evidence_count: int
    has_anomaly: bool
    has_trend: bool
    generated_at: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    anomaly: Optional[Dict[str, Any]] = None
    trend: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""

    verdict_status: str
    trust_score: float
    risk_level: str
    summary: str
    recommendations: List[Dict[str, Any]]
    suggested_interview_flow: List[str]
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str


# Initialize FastAPI app
app = FastAPI(
    title="Aegis Orchestrator API",
    description="Bayesian Orchestrator for AI Agent Fusion and Verdict Generation",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
bayesian_engine = BayesianEngine()
verdict_generator = VerdictGenerator(bayesian_engine)
recommendation_engine = RecommendationEngine()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Exception handlers
@app.exception_handler(OrchestratorError)
async def orchestrator_error_handler(request: Request, exc: OrchestratorError):
    """Handle orchestrator-specific errors"""
    logger.error(f"Orchestrator error: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message, "details": exc.details},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors"""
    logger.error(f"Value error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "details": str(exc)},
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
    )


@app.post("/verdict", response_model=VerdictResponse, tags=["Verdict"])
async def generate_verdict(request: VerdictRequest):
    """
    Generate authenticity verdict from agent results.

    Uses Bayesian fusion to combine agent results and generate a verdict
    with trust score, evidence, and reasoning.
    """
    try:
        # Update priors if provided
        if request.priors:
            bayesian_engine.update_priors(
                request.priors.alpha, request.priors.beta, request.priors.base_reliability
            )

        # Update weights if provided
        if request.weights:
            bayesian_engine.set_agent_weights(request.weights)

        # Convert request to AgentResult objects
        agent_results = [
            AgentResult(
                agent_id=r.agent_id,
                status=AgentStatus(r.status),
                score=r.score,
                confidence=r.confidence,
                data=r.data,
                metadata=r.metadata,
            )
            for r in request.agent_results
        ]

        # Generate verdict
        verdict = verdict_generator.generate_verdict(agent_results, request.history)

        # Convert evidence to dict
        evidence_dicts = [
            {
                "agent_id": e.agent_id,
                "score": e.score,
                "confidence": e.confidence,
                "weight": e.weight,
                "contribution": e.contribution,
                "details": e.details,
            }
            for e in verdict.evidence
        ]

        # Build response
        response = VerdictResponse(
            status=verdict.status.value,
            trust_score=verdict.trust_score,
            confidence=verdict.confidence,
            reasoning=verdict.reasoning,
            evidence_count=len(verdict.evidence),
            has_anomaly=verdict.anomaly is not None,
            has_trend=verdict.trend is not None,
            generated_at=verdict.generated_at.isoformat(),
            evidence=evidence_dicts,
            anomaly=verdict.anomaly,
            trend=verdict.trend,
            metadata=verdict.metadata,
        )

        logger.info(f"Generated verdict: {verdict.status.value} (trust={verdict.trust_score:.2f})")

        return response

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating verdict: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post(
    "/recommendations", response_model=RecommendationResponse, tags=["Recommendations"]
)
async def generate_recommendations(request: VerdictRequest):
    """
    Generate recommendations based on agent results.

    Provides actionable recommendations including suggested questions,
    flags, and interview flow guidance.
    """
    try:
        # Update priors if provided
        if request.priors:
            bayesian_engine.update_priors(
                request.priors.alpha, request.priors.beta, request.priors.base_reliability
            )

        # Update weights if provided
        if request.weights:
            bayesian_engine.set_agent_weights(request.weights)

        # Convert request to AgentResult objects
        agent_results = [
            AgentResult(
                agent_id=r.agent_id,
                status=AgentStatus(r.status),
                score=r.score,
                confidence=r.confidence,
                data=r.data,
                metadata=r.metadata,
            )
            for r in request.agent_results
        ]

        # Generate verdict first
        verdict = verdict_generator.generate_verdict(agent_results, request.history)

        # Generate recommendations
        report = recommendation_engine.generate_recommendations(verdict)

        # Convert recommendations to dict
        recommendation_dicts = [
            {
                "type": r.type.value,
                "priority": r.priority.value,
                "title": r.title,
                "description": r.description,
                "context": r.context,
                "suggested_questions": r.suggested_questions,
                "metadata": r.metadata,
            }
            for r in report.recommendations
        ]

        # Build response
        response = RecommendationResponse(
            verdict_status=report.verdict_status.value,
            trust_score=report.trust_score,
            risk_level=report.risk_level,
            summary=report.summary,
            recommendations=recommendation_dicts,
            suggested_interview_flow=report.suggested_interview_flow,
            metadata=report.metadata,
        )

        logger.info(
            f"Generated {len(report.recommendations)} recommendations for {report.verdict_status.value}"
        )

        return response

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analyze", tags=["Analysis"])
async def full_analysis(request: VerdictRequest):
    """
    Perform full analysis: verdict + recommendations.

    Returns both verdict and recommendations in a single response.
    """
    try:
        # Update priors if provided
        if request.priors:
            bayesian_engine.update_priors(
                request.priors.alpha, request.priors.beta, request.priors.base_reliability
            )

        # Update weights if provided
        if request.weights:
            bayesian_engine.set_agent_weights(request.weights)

        # Convert request to AgentResult objects
        agent_results = [
            AgentResult(
                agent_id=r.agent_id,
                status=AgentStatus(r.status),
                score=r.score,
                confidence=r.confidence,
                data=r.data,
                metadata=r.metadata,
            )
            for r in request.agent_results
        ]

        # Generate verdict
        verdict = verdict_generator.generate_verdict(agent_results, request.history)

        # Generate recommendations
        report = recommendation_engine.generate_recommendations(verdict)

        # Convert evidence to dict
        evidence_dicts = [
            {
                "agent_id": e.agent_id,
                "score": e.score,
                "confidence": e.confidence,
                "weight": e.weight,
                "contribution": e.contribution,
                "details": e.details,
            }
            for e in verdict.evidence
        ]

        # Convert recommendations to dict
        recommendation_dicts = [
            {
                "type": r.type.value,
                "priority": r.priority.value,
                "title": r.title,
                "description": r.description,
                "context": r.context,
                "suggested_questions": r.suggested_questions,
                "metadata": r.metadata,
            }
            for r in report.recommendations
        ]

        return {
            "verdict": {
                "status": verdict.status.value,
                "trust_score": verdict.trust_score,
                "confidence": verdict.confidence,
                "reasoning": verdict.reasoning,
                "evidence_count": len(verdict.evidence),
                "has_anomaly": verdict.anomaly is not None,
                "has_trend": verdict.trend is not None,
                "generated_at": verdict.generated_at.isoformat(),
                "evidence": evidence_dicts,
                "anomaly": verdict.anomaly,
                "trend": verdict.trend,
                "metadata": verdict.metadata,
            },
            "recommendations": {
                "verdict_status": report.verdict_status.value,
                "trust_score": report.trust_score,
                "risk_level": report.risk_level,
                "summary": report.summary,
                "recommendations": recommendation_dicts,
                "suggested_interview_flow": report.suggested_interview_flow,
                "metadata": report.metadata,
            },
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in full analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/config/priors", tags=["Configuration"])
async def get_priors():
    """Get current prior parameters"""
    return {
        "alpha": bayesian_engine.priors.alpha,
        "beta": bayesian_engine.priors.beta,
        "base_reliability": bayesian_engine.priors.base_reliability,
    }


@app.post("/config/priors", tags=["Configuration"])
async def update_priors(priors: PriorParameters):
    """Update prior parameters"""
    bayesian_engine.update_priors(priors.alpha, priors.beta, priors.base_reliability)
    logger.info(f"Updated priors: {priors}")
    return {"status": "success", "priors": priors}


@app.get("/config/weights", tags=["Configuration"])
async def get_weights():
    """Get current agent weights"""
    return {
        "chronos": bayesian_engine.weights.chronos,
        "echo": bayesian_engine.weights.echo,
        "iris": bayesian_engine.weights.iris,
        "lipsync": bayesian_engine.weights.lipsync,
        "nova": bayesian_engine.weights.nova,
    }


@app.post("/config/weights", tags=["Configuration"])
async def update_weights(weights: AgentWeights):
    """Update agent weights"""
    bayesian_engine.set_agent_weights(weights)
    logger.info(f"Updated weights: {weights}")
    return {"status": "success", "weights": weights}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
