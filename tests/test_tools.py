# ═══════════════════════════════════
# FILE: tests/test_tools.py
# PURPOSE: Unit tests for CrewAI tools
# ═══════════════════════════════════

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestApifyScraperTool:
    """Tests for the Apify Meta Ads scraper tool."""

    def test_mock_scrape_returns_valid_json(self):
        """When APIFY_API_TOKEN is empty, mock data should be returned."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key", "APIFY_API_TOKEN": ""}):
            from src.tools.apify_tool import ApifyScraperTool

            tool = ApifyScraperTool()
            result = tool._run(search_query="trading", max_ads=5)
            data = json.loads(result)

            assert isinstance(data, list)
            assert len(data) >= 3  # Mock returns 5 ads

            # Check first ad has required fields
            ad = data[0]
            assert "ad_id" in ad
            assert "advertiser_name" in ad
            assert "headline" in ad
            assert "hook" in ad
            assert "ad_copy" in ad
            assert "engagement_score" in ad
            assert 0.0 <= ad["engagement_score"] <= 1.0

    def test_mock_ads_have_niche_tags(self):
        """Mock ads should include niche tags."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key", "APIFY_API_TOKEN": ""}):
            from src.tools.apify_tool import ApifyScraperTool

            tool = ApifyScraperTool()
            result = tool._run(search_query="crypto", max_ads=5)
            data = json.loads(result)

            for ad in data:
                assert isinstance(ad["niche_tags"], list)


class TestFileIOTool:
    """Tests for the file I/O tool."""

    def test_save_and_load_json(self):
        """Should save JSON and load it back identically."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from src.tools.file_tool import FileIOTool

            tool = FileIOTool()

            with tempfile.TemporaryDirectory() as tmpdir:
                test_data = {"key": "value", "number": 42}
                filepath = os.path.join(tmpdir, "test_output.json")

                # Save
                save_result = tool._run(
                    data=json.dumps(test_data),
                    file_path=filepath,
                )
                assert "Saved to" in save_result

                # Load
                load_result = tool._run(data="", file_path=filepath)
                loaded = json.loads(load_result)
                assert loaded["key"] == "value"
                assert loaded["number"] == 42

    def test_load_nonexistent_file(self):
        """Should return an error message for missing files."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from src.tools.file_tool import FileIOTool

            tool = FileIOTool()
            result = tool._run(data="", file_path="/nonexistent/file.json")
            assert "Error" in result


class TestGDriveReaderTool:
    """Tests for the Google Drive reader tool."""

    def test_local_fallback(self):
        """When GDrive is not configured, should fall back to local files."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key",
            "GDRIVE_FOLDER_ID": "",
        }):
            from src.tools.gdrive_tool import GDriveReaderTool

            tool = GDriveReaderTool()
            result = tool._run(folder_id="")

            # Should contain some company info (from local fallback or default)
            assert "CrowdWisdomTrading" in result or "trading" in result.lower()


class TestElevenLabsTTSTool:
    """Tests for the ElevenLabs TTS tool."""

    def test_silent_fallback(self):
        """When ELEVENLABS_API_KEY is empty, should generate a silent placeholder."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key",
            "ELEVENLABS_API_KEY": "",
        }):
            from src.tools.elevenlabs_tool import ElevenLabsTTSTool

            tool = ElevenLabsTTSTool()

            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = os.path.join(tmpdir, "test_audio.mp3")
                result = tool._run(
                    text="This is a test sentence for audio.",
                    output_path=output_path,
                )

                assert Path(result).exists()
                assert Path(result).stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
