# ═══════════════════════════════════
# FILE: tests/test_agents.py
# PURPOSE: Unit tests for CrewAI agent creation
# ═══════════════════════════════════

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestAgentCreation:
    """Tests that all agents can be instantiated correctly."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Ensure required env vars are set for agent creation."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key-for-agents",
            "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
            "OPENROUTER_MODEL": "meta-llama/llama-3.3-70b-instruct:free",
        }):
            # Clear the settings cache so it picks up test env vars
            from src.config.settings import get_settings
            get_settings.cache_clear()
            yield
            get_settings.cache_clear()

    def test_ad_search_agent_creation(self):
        """Agent 1 should be created with correct role and tools."""
        from src.agents.ad_search_agent import create_ad_search_agent

        agent = create_ad_search_agent()
        assert agent.role == "Meta Ads Intelligence Specialist"
        assert len(agent.tools) == 2  # ApifyScraperTool + FileIOTool

    def test_marketing_agent_creation(self):
        """Agent 2 should be created with correct role."""
        from src.agents.marketing_agent import create_marketing_agent

        agent = create_marketing_agent()
        assert agent.role == "Direct Response Marketing Psychologist"
        assert len(agent.tools) == 1  # FileIOTool

    def test_script_agent_creation(self):
        """Agent 3 should be created with correct role and tools."""
        from src.agents.script_agent import create_script_agent

        agent = create_script_agent()
        assert agent.role == "Short-Form Video Ad Copywriter"
        assert len(agent.tools) == 2  # FileIOTool + GDriveReaderTool

    def test_video_agent_creation(self):
        """Agent 4 should be created with correct role and tools."""
        from src.agents.video_agent import create_video_agent

        agent = create_video_agent()
        assert agent.role == "AI Video Production Director"
        assert len(agent.tools) == 2  # ElevenLabsTTSTool + FileIOTool


class TestPydanticModels:
    """Tests for Pydantic data models."""

    def test_scraped_ad_model(self):
        """ScrapedAd should validate and serialize correctly."""
        from src.models.ad_models import ScrapedAd

        ad = ScrapedAd(
            ad_id="test_001",
            advertiser_name="Test Advertiser",
            headline="Test Headline",
            hook="This is a test hook.",
            ad_copy="Full ad copy here.",
            engagement_score=0.85,
            niche_tags=["trading", "crypto"],
        )

        assert ad.ad_id == "test_001"
        assert ad.engagement_score == 0.85
        data = ad.model_dump()
        assert data["niche_tags"] == ["trading", "crypto"]

    def test_marketing_analysis_model(self):
        """MarketingAnalysis should accept all expected fields."""
        from src.models.analysis_models import MarketingAnalysis

        analysis = MarketingAnalysis(
            pain_points=["losing money", "missing opportunities"],
            winning_hooks=[{"hook": "Test hook", "why_it_works": "It grabs attention"}],
            emotional_triggers=["FOMO", "fear"],
            urgency_tactics=["Limited time"],
            persuasion_patterns=["Problem-Agitate-Solve"],
            cta_analysis={"common_ctas": ["Sign Up"], "best_cta": "Sign Up Now"},
            audience_profile="Male traders 25-45",
            top_performing_ad_summary="Best ad summary",
            analyzed_at="2026-05-06T00:00:00Z",
        )

        assert len(analysis.pain_points) == 2
        assert analysis.audience_profile == "Male traders 25-45"

    def test_ad_script_model(self):
        """AdScript should accept nested Scene objects."""
        from src.models.script_models import AdScript, Scene

        scene = Scene(
            scene_number=1,
            scene_name="Hook",
            start_time_seconds=0,
            end_time_seconds=5,
            visual_direction="Close-up shot",
            voiceover="Are you tired of losing money?",
            subtitle_text="Are you tired of losing money?",
            duration_seconds=5,
        )

        script = AdScript(
            title="Test Script",
            total_duration_seconds=60,
            total_word_count=150,
            scenes=[scene],
        )

        assert script.scenes[0].scene_name == "Hook"
        assert script.total_duration_seconds == 60

    def test_job_record_model(self):
        """JobRecord should have sensible defaults."""
        from src.models.job_models import JobRecord, JobStatus

        job = JobRecord(job_id="test-uuid-123")
        assert job.status == JobStatus.QUEUED
        assert job.error is None
        assert job.created_at  # Should have a default timestamp


class TestTextUtils:
    """Tests for text utility functions."""

    def test_clean_text(self):
        """Should normalize whitespace and quotes."""
        from src.utils.text_utils import clean_text

        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("He said \u201chello\u201d") == 'He said "hello"'

    def test_estimate_duration(self):
        """Should estimate spoken duration based on word count."""
        from src.utils.text_utils import estimate_duration

        # 25 words at 2.5 wps = 10 seconds
        text = " ".join(["word"] * 25)
        assert estimate_duration(text) == 10.0

    def test_split_sentences(self):
        """Should split text into sentences on punctuation."""
        from src.utils.text_utils import split_sentences

        text = "First sentence. Second sentence! Third one?"
        sentences = split_sentences(text)
        assert len(sentences) == 3

    def test_word_count(self):
        """Should count words correctly."""
        from src.utils.text_utils import word_count

        assert word_count("hello world foo bar") == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
