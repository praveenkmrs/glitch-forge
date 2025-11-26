"""Structured logging configuration.

Production-ready logging with:
1. Structured JSON logs (easy to parse in log aggregators)
2. Different log levels per environment
3. Request ID tracking
4. Performance monitoring
"""

import logging
import sys
from typing import Any, Dict

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured data."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # In development, use human-readable format
        if settings.ENVIRONMENT == "development":
            return f"[{log_data['level']}] {log_data['logger']}: {log_data['message']}"

        # In production, use JSON for log aggregators
        import json
        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        force=True,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
