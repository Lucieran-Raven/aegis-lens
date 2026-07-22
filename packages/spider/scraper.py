"""Web scraping module"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ScrapedData:
    """Represents scraped data"""

    url: str
    title: str
    content: str
    metadata: dict
    scraped_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "scraped_at": self.scraped_at.isoformat(),
        }


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""

    success: bool
    data: Optional[ScrapedData]
    error: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data.to_dict() if self.data else None,
            "error": self.error,
        }
