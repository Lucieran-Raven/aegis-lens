"""
Logging Configuration for Orchestrator

This module provides structured logging configuration for the orchestrator service.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""

    grey = "\x1b[38;20m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        import json

        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_obj["extra"] = record.extra

        return json.dumps(log_obj)


def configure_logging(
    level: str = "INFO",
    format_type: str = "colored",
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging for the orchestrator.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type (colored, json, simple)
        log_file: Optional log file path
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if format_type == "colored":
        console_handler.setFormatter(ColoredFormatter())
    elif format_type == "json":
        console_handler.setFormatter(JSONFormatter())
    else:  # simple
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(file_handler)

    # Configure specific loggers
    configure_logger_levels(numeric_level)


def configure_logger_levels(level: int) -> None:
    """
    Configure specific logger levels.

    Args:
        level: Numeric logging level
    """
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Set orchestrator loggers
    logging.getLogger("src.orchestrator").setLevel(level)
    logging.getLogger("src.orchestrator.bayesian_engine").setLevel(level)
    logging.getLogger("src.orchestrator.verdict").setLevel(level)
    logging.getLogger("src.orchestrator.recommendation").setLevel(level)
    logging.getLogger("src.orchestrator.api").setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class OrchestratorLogger:
    """
    Orchestrator-specific logger with structured logging capabilities.
    """

    def __init__(self, name: str):
        """
        Initialize orchestrator logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)

    def debug(self, message: str, **kwargs):
        """Log debug message with extra context"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with extra context"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with extra context"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with extra context"""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with extra context"""
        self.logger.critical(message, extra=kwargs)

    def log_agent_result(self, agent_id: str, score: float, confidence: float, **kwargs):
        """Log agent result with structured data"""
        self.info(
            f"Agent result: {agent_id}",
            agent_id=agent_id,
            score=score,
            confidence=confidence,
            **kwargs,
        )

    def log_verdict(self, status: str, trust_score: float, **kwargs):
        """Log verdict with structured data"""
        self.info(
            f"Verdict generated: {status}",
            status=status,
            trust_score=trust_score,
            **kwargs,
        )

    def log_recommendation(self, count: int, risk_level: str, **kwargs):
        """Log recommendation with structured data"""
        self.info(
            f"Recommendations generated: {count}",
            recommendation_count=count,
            risk_level=risk_level,
            **kwargs,
        )

    def log_error_with_context(self, error: Exception, context: dict):
        """Log error with additional context"""
        self.error(
            f"Error occurred: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
        )
