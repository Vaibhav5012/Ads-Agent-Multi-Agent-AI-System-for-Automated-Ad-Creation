# ═══════════════════════════════════
# FILE: src/api/__init__.py
# PURPOSE: API package marker
# ═══════════════════════════════════

from src.api.app import create_app

__all__ = ["create_app"]
