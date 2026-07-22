"""Tests for biometrics module"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from biometrics import BiometricData, AuthenticationResult


def test_biometric_data_creation():
    """Test biometric data creation"""
    data = BiometricData(
        user_id="user-1",
        biometric_type="face",
        data_hash="abc123",
        confidence=0.9,
    )
    assert data.user_id == "user-1"
    assert data.confidence == 0.9


def test_biometric_verify():
    """Test biometric verification"""
    data = BiometricData(
        user_id="user-1",
        biometric_type="face",
        data_hash="abc123",
        confidence=0.9,
    )
    assert data.verify() is True
    assert data.verify(threshold=0.95) is False


def test_authentication_result():
    """Test authentication result"""
    result = AuthenticationResult(
        success=True,
        user_id="user-1",
        confidence=0.9,
        timestamp="2024-01-01T00:00:00Z",
    )
    assert result.success is True
    assert result.user_id == "user-1"


def test_authentication_result_to_dict():
    """Test authentication result to dictionary"""
    result = AuthenticationResult(
        success=True,
        user_id="user-1",
        confidence=0.9,
        timestamp="2024-01-01T00:00:00Z",
    )
    data = result.to_dict()
    assert data["success"] is True
    assert data["user_id"] == "user-1"
