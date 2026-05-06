# ═══════════════════════════════════
# FILE: src/tools/file_tool.py
# PURPOSE: CrewAI Tool — save and load JSON files
# ═══════════════════════════════════

from __future__ import annotations

import json
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.utils.file_utils import save_json, load_json
from src.utils.logger import get_logger

logger = get_logger()


class SaveFileInputSchema(BaseModel):
    """Input schema for saving data to a JSON file."""

    data: str = Field(..., description="JSON string of data to save")
    file_path: str = Field(..., description="Destination file path")


class LoadFileInputSchema(BaseModel):
    """Input schema for loading data from a JSON file."""

    file_path: str = Field(..., description="Path to the JSON file to load")


class FileIOTool(BaseTool):
    """Saves and loads JSON data to/from the filesystem."""

    name: str = "File IO"
    description: str = (
        "Saves JSON data to a file or loads data from an existing JSON file. "
        "Pass a JSON string as 'data' and a 'file_path' to save, "
        "or just a 'file_path' to load."
    )
    args_schema: type[BaseModel] = SaveFileInputSchema

    def _run(self, data: str = "", file_path: str = "") -> str:
        """Save or load JSON data."""
        if not file_path:
            return "Error: file_path is required"

        path = Path(file_path)

        # If data is provided, we save; otherwise we load
        if data:
            return self._save(data, path)
        else:
            return self._load(path)

    def _save(self, data_str: str, path: Path) -> str:
        """Parse JSON string and save to file."""
        try:
            parsed = json.loads(data_str)
        except json.JSONDecodeError:
            # If it's not valid JSON, wrap it
            parsed = {"raw_content": data_str}

        saved_path = save_json(parsed, path)
        return f"Saved to {saved_path}"

    def _load(self, path: Path) -> str:
        """Load JSON from file and return as string."""
        try:
            data = load_json(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            return f"Error: File not found — {path}"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in {path} — {e}"
