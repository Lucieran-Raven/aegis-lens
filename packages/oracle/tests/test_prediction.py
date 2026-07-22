"""Tests for prediction module"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime
from prediction import Prediction, Forecast


def test_prediction_creation():
    """Test prediction creation"""
    prediction = Prediction(
        target="hiring",
        predicted_value=100,
        confidence=0.85,
        timestamp=datetime.now(),
    )
    assert prediction.target == "hiring"
    assert prediction.predicted_value == 100


def test_prediction_to_dict():
    """Test prediction to dictionary"""
    prediction = Prediction(
        target="hiring",
        predicted_value=100,
        confidence=0.85,
        timestamp=datetime.now(),
    )
    data = prediction.to_dict()
    assert data["target"] == "hiring"
    assert data["predicted_value"] == 100


def test_forecast():
    """Test forecast operations"""
    forecast = Forecast(target="hiring", predictions=[], model_version="v1")
    prediction = Prediction(
        target="hiring",
        predicted_value=100,
        confidence=0.85,
        timestamp=datetime.now(),
    )
    forecast.add_prediction(prediction)
    assert len(forecast.predictions) == 1
    assert forecast.get_latest_prediction() == prediction


def test_forecast_empty():
    """Test forecast with no predictions"""
    forecast = Forecast(target="hiring", predictions=[], model_version="v1")
    assert forecast.get_latest_prediction() is None
