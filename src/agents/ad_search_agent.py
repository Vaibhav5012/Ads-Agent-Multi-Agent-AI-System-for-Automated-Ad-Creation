# ═══════════════════════════════════
# FILE: src/agents/ad_search_agent.py
# PURPOSE: Agent 1 — Meta Ads Intelligence Specialist
# ═══════════════════════════════════

from __future__ import annotations

from crewai import Agent, LLM

from src.config.settings import get_settings
from src.tools.apify_tool import ApifyScraperTool
from src.tools.file_tool import FileIOTool


def _build_llm() -> LLM:
    """Construct the LLM instance for this agent via CrewAI's native LLM class."""
    settings = get_settings()
    return LLM(
        model=f"openrouter/{settings.openrouter_model}",
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.7,
        max_tokens=4096,
    )


def create_ad_search_agent() -> Agent:
    """
    Create the **Ad Search Agent** (Agent 1).

    Role: Meta Ads Intelligence Specialist
    Goal: Find and rank the top 10 highest-performing trading/finance ads
          from the Meta Ad Library (last 30 days).
    """
    return Agent(
        role="Meta Ads Intelligence Specialist",
        goal=(
            "Find the top 10 highest-performing trading and finance ads "
            "from the Meta Ad Library that were active in the last 30 days. "
            "Score them by engagement signals, copy quality, and emotional "
            "language presence. Save the ranked results to a JSON file."
        ),
        backstory=(
            "You are a seasoned digital marketing researcher who has spent "
            "a decade analysing paid social ads in the finance and trading niche. "
            "You know exactly what separates a high-converting ad from a dud: "
            "the hook, the emotional triggers, the proof elements, and the CTA. "
            "You have access to the Meta Ad Library through Apify and can "
            "efficiently scrape, parse, and rank ads by their likely performance."
        ),
        tools=[ApifyScraperTool(), FileIOTool()],
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )
