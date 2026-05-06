# ═══════════════════════════════════
# FILE: src/utils/retry_utils.py
# PURPOSE: Tenacity retry decorators for resilient API calls
# ═══════════════════════════════════

from __future__ import annotations

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)
import httpx
import logging

# Tenacity wants a stdlib logger for before_sleep_log
_std_logger = logging.getLogger("cwt.retry")


def retry_on_failure(
    max_attempts: int = 3,
    min_wait: int = 2,
    max_wait: int = 10,
):
    """
    Decorator factory that retries on transient errors using exponential backoff.

    Usage::

        @retry_on_failure(max_attempts=3)
        def call_external_api(...):
            ...
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, TimeoutError, Exception)),
        reraise=True,
        before_sleep=before_sleep_log(_std_logger, logging.WARNING),
    )
