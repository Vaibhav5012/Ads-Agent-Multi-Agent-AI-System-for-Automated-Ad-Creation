# ═══════════════════════════════════
# FILE: src/utils/file_utils.py
# PURPOSE: JSON file helpers — save, load, timestamped paths
# ═══════════════════════════════════

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger

logger = get_logger()


def timestamped_path(directory: Path | str, prefix: str, extension: str = ".json") -> Path:
    """Return a path like ``directory/prefix_20260506_120000.json``."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{prefix}_{ts}{extension}"


def save_json(data: Any, path: Path | str) -> str:
    """Serialise *data* to a JSON file and return the absolute path as a string."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Handle Pydantic models
    if hasattr(data, "model_dump"):
        data = data.model_dump(mode="json")
    elif hasattr(data, "dict"):
        data = data.dict()

    # Handle lists of Pydantic models
    if isinstance(data, list):
        data = [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in data
        ]

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Saved JSON → {path}")
    return str(path.resolve())


def load_json(path: Path | str) -> Any:
    """Load and return data from a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    logger.info(f"Loaded JSON ← {path}")
    return data
