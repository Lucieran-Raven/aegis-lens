"""Tests for scoring module"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from scoring import CandidateScore, calculate_overall_score


def test_candidate_score_creation():
    """Test candidate score creation"""
    score = CandidateScore(
        candidate_id="test-1",
        overall_score=0.85,
        skills_score=0.9,
        experience_score=0.8,
        cultural_fit=0.85,
    )
    assert score.candidate_id == "test-1"
    assert score.overall_score == 0.85


def test_candidate_score_to_dict():
    """Test conversion to dictionary"""
    score = CandidateScore(
        candidate_id="test-1",
        overall_score=0.85,
        skills_score=0.9,
        experience_score=0.8,
        cultural_fit=0.85,
    )
    data = score.to_dict()
    assert data["candidate_id"] == "test-1"
    assert data["overall_score"] == 0.85


def test_candidate_score_from_dict():
    """Test creation from dictionary"""
    data = {
        "candidate_id": "test-1",
        "overall_score": 0.85,
        "skills_score": 0.9,
        "experience_score": 0.8,
        "cultural_fit": 0.85,
    }
    score = CandidateScore.from_dict(data)
    assert score.candidate_id == "test-1"
    assert score.overall_score == 0.85


def test_calculate_overall_score():
    """Test overall score calculation"""
    score = calculate_overall_score(0.9, 0.8, 0.85)
    expected = (0.9 * 0.4) + (0.8 * 0.4) + (0.85 * 0.2)
    assert abs(score - expected) < 0.01
