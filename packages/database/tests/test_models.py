"""
Tests for database models
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from models.base import Base
from models.candidate import Candidate
from models.session import Session
from models.agent_result import AgentResult
from models.intelligence import Intelligence


def test_candidate_model(db_session):
    """Test Candidate model creation and retrieval"""
    
    # Create a candidate
    candidate = Candidate(
        id="test-candidate-1",
        email_hash="abc123def456",
        position_applied="Software Engineer",
        status="pending"
    )
    
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    
    # Retrieve the candidate
    result = db_session.execute(
        select(Candidate).where(Candidate.id == "test-candidate-1")
    )
    retrieved = result.scalar_one()
    
    assert retrieved.id == "test-candidate-1"
    assert retrieved.email_hash == "abc123def456"
    assert retrieved.position_applied == "Software Engineer"
    assert retrieved.status == "pending"
    assert retrieved.created_at is not None
    assert retrieved.updated_at is not None


def test_session_model(db_session):
    """Test Session model creation and retrieval"""
    
    # Create a candidate first
    candidate = Candidate(
        id="test-candidate-2",
        email_hash="xyz789abc123",
        position_applied="Data Scientist",
        status="active"
    )
    db_session.add(candidate)
    db_session.commit()
    
    # Create a session
    session = Session(
        id="test-session-1",
        candidate_id="test-candidate-2",
        started_at=datetime.now(timezone.utc),
        status="in_progress",
        interview_type="technical"
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Retrieve the session
    result = db_session.execute(
        select(Session).where(Session.id == "test-session-1")
    )
    retrieved = result.scalar_one()
    
    assert retrieved.id == "test-session-1"
    assert retrieved.candidate_id == "test-candidate-2"
    assert retrieved.status == "in_progress"
    assert retrieved.interview_type == "technical"


def test_agent_result_model(db_session):
    """Test AgentResult model creation and retrieval"""
    
    # Create candidate and session
    candidate = Candidate(
        id="test-candidate-3",
        email_hash="def456ghi789",
        position_applied="Backend Engineer",
        status="active"
    )
    db_session.add(candidate)
    
    session = Session(
        id="test-session-2",
        candidate_id="test-candidate-3",
        started_at=datetime.now(timezone.utc),
        status="in_progress"
    )
    db_session.add(session)
    db_session.commit()
    
    # Create agent result
    agent_result = AgentResult(
        id="test-result-1",
        session_id="test-session-2",
        agent_name="chronos",
        agent_type="physics",
        analyzed_at=datetime.now(timezone.utc),
        score=0.85,
        confidence=0.92,
        status="clear",
        metrics={"mean_jitter": 15.2, "std_jitter": 2.8}
    )
    db_session.add(agent_result)
    db_session.commit()
    db_session.refresh(agent_result)
    
    # Retrieve the agent result
    result = db_session.execute(
        select(AgentResult).where(AgentResult.id == "test-result-1")
    )
    retrieved = result.scalar_one()
    
    assert retrieved.id == "test-result-1"
    assert retrieved.agent_name == "chronos"
    assert retrieved.agent_type == "physics"
    assert retrieved.score == 0.85
    assert retrieved.confidence == 0.92
    assert retrieved.status == "clear"
    assert retrieved.metrics["mean_jitter"] == 15.2


def test_intelligence_model(db_session):
    """Test Intelligence model creation and retrieval"""
    
    # Create candidate
    candidate = Candidate(
        id="test-candidate-4",
        email_hash="ghi789jkl012",
        position_applied="Full Stack Developer",
        status="pending"
    )
    db_session.add(candidate)
    db_session.commit()
    
    # Create intelligence
    intelligence = Intelligence(
        id="test-intel-1",
        candidate_id="test-candidate-4",
        source="linkedin",
        intel_type="employment",
        data={
            "company": "Tech Corp",
            "position": "Senior Developer",
            "start_date": "2020-01-01",
            "end_date": "2022-12-31"
        },
        confidence=0.95,
        relevance=0.9,
        is_verified=True
    )
    db_session.add(intelligence)
    db_session.commit()
    db_session.refresh(intelligence)
    
    # Retrieve the intelligence
    result = db_session.execute(
        select(Intelligence).where(Intelligence.id == "test-intel-1")
    )
    retrieved = result.scalar_one()
    
    assert retrieved.id == "test-intel-1"
    assert retrieved.candidate_id == "test-candidate-4"
    assert retrieved.source == "linkedin"
    assert retrieved.intel_type == "employment"
    assert retrieved.confidence == 0.95
    assert retrieved.is_verified is True
