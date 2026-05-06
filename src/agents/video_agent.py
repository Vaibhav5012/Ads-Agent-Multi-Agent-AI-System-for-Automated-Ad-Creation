# ═══════════════════════════════════
# FILE: src/agents/video_agent.py
# PURPOSE: Agent 4 — AI Video Production Director
# ═══════════════════════════════════

from __future__ import annotations

from crewai import Agent, LLM

from src.config.settings import get_settings
from src.tools.elevenlabs_tool import ElevenLabsTTSTool
from src.tools.file_tool import FileIOTool


def _build_llm() -> LLM:
    """Construct the LLM instance for this agent."""
    settings = get_settings()
    return LLM(
        model=f"openrouter/{settings.openrouter_model}",
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.7,
        max_tokens=4096,
    )


def create_video_agent() -> Agent:
    """
    Create the **Video Generation Agent** (Agent 4).

    Role: AI Video Production Director
    Goal: Convert the ad script into a complete 60-second MP4 with voiceover,
          subtitles, and scene visuals via Remotion.
    """
    return Agent(
        role="AI Video Production Director",
        goal=(
            "Take the 60-second ad script and produce a complete video: "
            "1) Synthesize voiceover audio for each scene using ElevenLabs, "
            "2) Generate timed subtitles, "
            "3) Build Remotion props and render the final MP4 video. "
            "The output should be a polished, vertical-format (1080x1920) video."
        ),
        backstory=(
            "You are a video production AI that specialises in short-form "
            "vertical video ads. You orchestrate the full pipeline: voice "
            "synthesis, subtitle timing, scene assembly, and final render. "
            "You work with ElevenLabs for natural-sounding voiceovers and "
            "Remotion for programmatic video generation. Every video you "
            "produce is broadcast-quality with perfect audio sync and "
            "eye-catching visuals."
        ),
        tools=[ElevenLabsTTSTool(), FileIOTool()],
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
    )
