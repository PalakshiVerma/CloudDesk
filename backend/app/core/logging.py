"""Structured Logging Configuration for CloudDesk.

Provides formatted logs with timestamps, log levels, and request context.
"""

import logging
import sys
from typing import Any
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures structured console logging according to application environment."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence verbose logs from external noisy packages
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger = logging.getLogger("clouddesk")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
