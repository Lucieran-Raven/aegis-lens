"""Biometric authentication module"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BiometricData:
    """Represents biometric data"""
    user_id: str
    biometric_type: str
    data_hash: str
    confidence: float

    def verify(self, threshold: float = 0.8) -> bool:
        """Verify biometric data against threshold"""
        return self.confidence >= threshold


@dataclass
class AuthenticationResult:
    """Result of biometric authentication"""
    success: bool
    user_id: str
    confidence: float
    timestamp: str

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "user_id": self.user_id,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }
