# ═══════════════════════════════════
# FILE: src/api/dependencies.py
# PURPOSE: FastAPI Depends() helpers
# ═══════════════════════════════════

from __future__ import annotations

from functools import lru_cache

from tinydb import TinyDB

from src.config.settings import get_settings


@lru_cache(maxsize=1)
def _get_tinydb_instance() -> TinyDB:
    """Create or return the TinyDB singleton for job tracking."""
    settings = get_settings()
    db_path = settings.jobs_db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return TinyDB(str(db_path))


def get_db() -> TinyDB:
    """FastAPI dependency that provides the TinyDB instance."""
    return _get_tinydb_instance()
