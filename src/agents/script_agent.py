# ═══════════════════════════════════
# FILE: src/agents/script_agent.py
# PURPOSE: Agent 3 — Short-Form Video Ad Copywriter
# ═══════════════════════════════════

from __future__ import annotations

from crewai import Agent, LLM

from src.config.settings import get_settings
from src.tools.file_tool import FileIOTool
from src.tools.gdrive_tool import GDriveReaderTool


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


def create_script_agent() -> Agent:
    """
    Create the **Script Generation Agent** (Agent 3).

    Role: Short-Form Video Ad Copywriter
    Goal: Write a 60-second TikTok/Reels-style video ad script for
          CrowdWisdomTrading using marketing intelligence + company data.
    """
    return Agent(
        role="Short-Form Video Ad Copywriter",
        goal=(
            "Write a compelling 60-second video ad script for CrowdWisdomTrading "
            "with exactly 6 scenes (Hook, Pain Point, Agitation, Solution Reveal, "
            "Social Proof, CTA). The script must use the marketing intelligence "
            "from the analysis and the company's unique value proposition. "
            "Total voiceover should be 140-160 words."
        ),
        backstory=(
            "You are an elite short-form video ad copywriter who creates 60-second "
            "scripts that stop the scroll, trigger emotion, and convert cold traffic. "
            "You have written viral ad scripts for DTC brands, fintech startups, and "
            "trading education companies. Your scripts consistently achieve 3x+ ROAS. "
            "You think in hooks, pain loops, and pattern interrupts. You never sound "
            "salesy — instead, you write like a trusted friend giving urgent advice."
        ),
        tools=[FileIOTool(), GDriveReaderTool()],
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )
