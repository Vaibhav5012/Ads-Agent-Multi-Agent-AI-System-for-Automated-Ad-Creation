# ═══════════════════════════════════
# FILE: src/utils/logger.py
# PURPOSE: Loguru-based logging setup with structured output
# ═══════════════════════════════════

from __future__ import annotations

import sys
from functools import lru_cache

from loguru import logger


def _configure_logger(level: str = "INFO") -> None:
    """Remove default handlers and add custom formatted ones."""
    logger.remove()

    # Console handler — coloured, human-readable
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler — JSON-structured for production
    logger.add(
        "logs/cwt_{time:YYYY-MM-DD}.log",
        level=level.upper(),
        rotation="10 MB",
        retention="7 days",
        compression="gz",
        serialize=True,
    )


@lru_cache(maxsize=1)
def get_logger(level: str = "INFO") -> logger.__class__:
    """Return the pre-configured Loguru logger singleton."""
    _configure_logger(level)
    return logger
