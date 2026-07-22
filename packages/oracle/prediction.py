"""Predictive analytics module"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Prediction:
    """Represents a prediction result"""

    target: str
    predicted_value: float
    confidence: float
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "target": self.target,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Forecast:
    """Represents a forecast with multiple predictions"""

    target: str
    predictions: List[Prediction]
    model_version: str

    def add_prediction(self, prediction: Prediction) -> None:
        """Add a prediction to the forecast"""
        self.predictions.append(prediction)

    def get_latest_prediction(self) -> Optional[Prediction]:
        """Get the latest prediction"""
        if self.predictions:
            return self.predictions[-1]
        return None
