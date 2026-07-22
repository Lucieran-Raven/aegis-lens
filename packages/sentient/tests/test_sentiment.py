"""Tests for sentiment module"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sentiment import Sentiment, SentimentResult, analyze_sentiment


def test_sentiment_enum():
    """Test sentiment enum"""
    assert Sentiment.POSITIVE.value == "positive"
    assert Sentiment.NEGATIVE.value == "negative"
    assert Sentiment.NEUTRAL.value == "neutral"


def test_sentiment_result_creation():
    """Test sentiment result creation"""
    result = SentimentResult(
        text="test",
        sentiment=Sentiment.POSITIVE,
        confidence=0.9,
        emotions={"joy": 0.8},
    )
    assert result.text == "test"
    assert result.sentiment == Sentiment.POSITIVE


def test_sentiment_result_to_dict():
    """Test conversion to dictionary"""
    result = SentimentResult(
        text="test",
        sentiment=Sentiment.POSITIVE,
        confidence=0.9,
        emotions={"joy": 0.8},
    )
    data = result.to_dict()
    assert data["sentiment"] == "positive"
    assert data["confidence"] == 0.9


def test_analyze_sentiment():
    """Test sentiment analysis"""
    result = analyze_sentiment("test text")
    assert result.text == "test text"
    assert result.sentiment == Sentiment.NEUTRAL
