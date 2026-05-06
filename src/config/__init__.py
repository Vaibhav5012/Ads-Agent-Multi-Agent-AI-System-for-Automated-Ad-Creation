# ═══════════════════════════════════
# FILE: src/config/__init__.py
# PURPOSE: Config package marker
# ═══════════════════════════════════

from src.config.settings import get_settings, Settings

__all__ = ["get_settings", "Settings"]
