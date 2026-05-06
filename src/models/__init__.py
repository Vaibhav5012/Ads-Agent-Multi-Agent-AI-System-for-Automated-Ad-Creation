# ═══════════════════════════════════
# FILE: src/models/__init__.py
# PURPOSE: Models package marker
# ═══════════════════════════════════

from src.models.ad_models import ScrapedAd, AdCollection
from src.models.analysis_models import MarketingAnalysis, PainPoint, Hook
from src.models.script_models import AdScript, Scene, VoiceoverSegment
from src.models.job_models import JobStatus, JobResult, JobRecord

__all__ = [
    "ScrapedAd",
    "AdCollection",
    "MarketingAnalysis",
    "PainPoint",
    "Hook",
    "AdScript",
    "Scene",
    "VoiceoverSegment",
    "JobStatus",
    "JobResult",
    "JobRecord",
]
