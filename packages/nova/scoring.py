"""Candidate scoring and assessment module"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CandidateScore:
    """Represents a candidate's assessment score"""

    candidate_id: str
    overall_score: float
    skills_score: float
    experience_score: float
    cultural_fit: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "candidate_id": self.candidate_id,
            "overall_score": self.overall_score,
            "skills_score": self.skills_score,
            "experience_score": self.experience_score,
            "cultural_fit": self.cultural_fit,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateScore":
        """Create from dictionary"""
        return cls(
            candidate_id=data["candidate_id"],
            overall_score=data["overall_score"],
            skills_score=data["skills_score"],
            experience_score=data["experience_score"],
            cultural_fit=data["cultural_fit"],
        )


def calculate_overall_score(
    skills: float, experience: float, cultural_fit: float
) -> float:
    """Calculate weighted overall score"""
    return (skills * 0.4) + (experience * 0.4) + (cultural_fit * 0.2)
