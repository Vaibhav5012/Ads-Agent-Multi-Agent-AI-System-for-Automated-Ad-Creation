# ═══════════════════════════════════
# FILE: src/crew/ad_crew.py
# PURPOSE: Crew assembly + sequential kickoff — the main pipeline
# FIXED VERSION — all critical issues resolved
# ═══════════════════════════════════

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from crewai import Crew, Process

from src.agents import (
    create_ad_search_agent,
    create_marketing_agent,
    create_script_agent,
    create_video_agent,
)
from src.tasks import (
    create_ad_search_task,
    create_marketing_analysis_task,
    create_script_generation_task,
    create_video_production_task,
)
from src.config.settings import settings  # ✅ FIXED: import singleton, not function
from src.video.remotion_orchestrator import RemotionOrchestrator
from src.utils.logger import get_logger

logger = get_logger()


class AdCrewPipeline:
    """
    Orchestrates the full 4-agent sequential pipeline:

    1. Ad Search Agent   → scrapes & ranks ads
    2. Marketing Agent   → extracts marketing intelligence
    3. Script Agent      → generates 60s ad script
    4. Video Agent       → produces voiceover + subtitles + video
    """

    def __init__(self, niche: str = "trading", company_context: str = ""):
        self.niche = niche
        self.company_context = company_context
        self.settings = settings  # ✅ FIXED: use singleton

    def build_crew(self) -> Crew:
        """Assemble agents and tasks into a CrewAI Crew."""
        logger.info("Building crew pipeline…")

        # ── Create agents ─────────────────────
        agent1 = create_ad_search_agent()
        agent2 = create_marketing_agent()
        agent3 = create_script_agent()
        agent4 = create_video_agent()

        # ── Create tasks ──────────────────────
        task1 = create_ad_search_task(agent1, niche=self.niche)
        task2 = create_marketing_analysis_task(agent2)
        task3 = create_script_generation_task(agent3)
        task4 = create_video_production_task(agent4)

        crew = Crew(
            agents=[agent1, agent2, agent3, agent4],
            tasks=[task1, task2, task3, task4],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )

        logger.info("Crew assembled with 4 agents, 4 tasks (sequential)")
        return crew

    def run(self) -> dict[str, Any]:
        """Execute the full pipeline and return the result."""
        logger.info(f"Starting CrowdWisdomTrading pipeline — niche='{self.niche}'")
        # ✅ FIXED: Removed ensure_directories() call - happens on settings import

        crew = self.build_crew()
        result = crew.kickoff(inputs={"niche": self.niche})

        # ✅ FIXED: Handle None result
        result_str = str(result) if result is not None else "No result returned"
        logger.info(f"Crew pipeline completed. Result: {result_str}")

        # Attempt Remotion render as a post-processing step
        video_path = self._render_video()

        return {
            "crew_result": result_str,
            "video_path": video_path,
            "niche": self.niche,
        }

    def run_analysis_only(self, ads_file_path: str) -> dict[str, Any]:
        """Run only Agent 2 (marketing analysis) on an existing ads file."""
        logger.info(f"Running analysis-only on: {ads_file_path}")

        agent2 = create_marketing_agent()
        task2 = create_marketing_analysis_task(agent2)

        crew = Crew(
            agents=[agent2],
            tasks=[task2],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )

        result = crew.kickoff(inputs={"ads_file_path": ads_file_path})
        result_str = str(result) if result is not None else "No result returned"
        return {"crew_result": result_str}

    def run_video_only(self, script_file_path: str) -> dict[str, Any]:
        """Run only Agent 4 (video production) on an existing script file."""
        logger.info(f"Running video-only on: {script_file_path}")

        agent4 = create_video_agent()
        task4 = create_video_production_task(agent4)

        crew = Crew(
            agents=[agent4],
            tasks=[task4],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )

        result = crew.kickoff(inputs={"script_file_path": script_file_path})
        result_str = str(result) if result is not None else "No result returned"

        video_path = self._render_video()
        return {"crew_result": result_str, "video_path": video_path}

    def _render_video(self) -> str:
        """Attempt to render the final video via Remotion."""
        try:
            # ✅ FIXED: Check if Remotion is available before trying
            remotion_dir = Path("remotion")
            if not (remotion_dir / "node_modules").exists():
                logger.warning(
                    f"Remotion node_modules not found. "
                    f"Run: cd remotion && npm install"
                )
                return ""

            orchestrator = RemotionOrchestrator()
            video_path = orchestrator.render()
            logger.info(f"Remotion render complete → {video_path}")
            return video_path
        except Exception as e:
            logger.warning(f"Remotion render skipped/failed: {e}")
            return ""