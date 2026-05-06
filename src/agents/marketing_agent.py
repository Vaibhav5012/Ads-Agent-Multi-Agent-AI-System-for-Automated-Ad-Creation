# ═══════════════════════════════════
# FILE: src/agents/marketing_agent.py
# PURPOSE: Agent 2 — Direct Response Marketing Psychologist
# ═══════════════════════════════════

from __future__ import annotations

from crewai import Agent, LLM

from src.config.settings import get_settings
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


def create_marketing_agent() -> Agent:
    """
    Create the **Marketing Analysis Agent** (Agent 2).

    Role: Direct Response Marketing Psychologist
    Goal: Extract and structure marketing intelligence from scraped ads.
    """
    return Agent(
        role="Direct Response Marketing Psychologist",
        goal=(
            "Analyse the scraped trading/finance ads and extract deep marketing "
            "intelligence: pain points, winning hooks, emotional triggers, "
            "urgency tactics, persuasion patterns, CTA analysis, and audience profile. "
            "Return structured JSON that the script writer can use."
        ),
        backstory=(
            "You are a world-class direct response marketing analyst specialising "
            "in financial products, trading education, and wealth-building offers. "
            "You have reverse-engineered thousands of high-performing ads and can "
            "instantly identify the psychological levers that make them convert. "
            "Your analysis is precise, specific, and actionable — never generic."
        ),
        tools=[FileIOTool()],
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )
