# ═══════════════════════════════════
# FILE: src/tasks/__init__.py
# PURPOSE: Tasks package marker
# ═══════════════════════════════════

from src.tasks.task_definitions import (
    create_ad_search_task,
    create_marketing_analysis_task,
    create_script_generation_task,
    create_video_production_task,
)

__all__ = [
    "create_ad_search_task",
    "create_marketing_analysis_task",
    "create_script_generation_task",
    "create_video_production_task",
]
