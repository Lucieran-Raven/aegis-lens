"""Tests for scraper module"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime
from scraper import ScrapedData, ScrapingResult


def test_scraped_data_creation():
    """Test scraped data creation"""
    data = ScrapedData(
        url="https://example.com",
        title="Example",
        content="Content",
        metadata={},
        scraped_at=datetime.now(),
    )
    assert data.url == "https://example.com"
    assert data.title == "Example"


def test_scraped_data_to_dict():
    """Test scraped data to dictionary"""
    data = ScrapedData(
        url="https://example.com",
        title="Example",
        content="Content",
        metadata={},
        scraped_at=datetime.now(),
    )
    dict_data = data.to_dict()
    assert dict_data["url"] == "https://example.com"
    assert "scraped_at" in dict_data


def test_scraping_result():
    """Test scraping result"""
    data = ScrapedData(
        url="https://example.com",
        title="Example",
        content="Content",
        metadata={},
        scraped_at=datetime.now(),
    )
    result = ScrapingResult(success=True, data=data, error=None)
    assert result.success is True
    assert result.data is not None


def test_scraping_result_error():
    """Test scraping result with error"""
    result = ScrapingResult(success=False, data=None, error="Network error")
    assert result.success is False
    assert result.error == "Network error"
