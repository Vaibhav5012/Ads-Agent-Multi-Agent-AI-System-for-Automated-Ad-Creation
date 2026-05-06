# ═══════════════════════════════════
# FILE: src/api/background_tasks.py
# PURPOSE: BackgroundTasks job runners for the FastAPI endpoints
# FIXED VERSION — DB connection handling corrected
# ═══════════════════════════════════

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from tinydb import TinyDB, Query

from src.crew.ad_crew import AdCrewPipeline
from src.models.job_models import JobStatus
from src.utils.logger import get_logger

logger = get_logger()
Job = Query()


def _get_db() -> TinyDB:
    """Create a fresh DB connection. Called within each background task."""
    db_path = Path("data") / "jobs.json"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return TinyDB(str(db_path))


def _update_job(db: TinyDB, job_id: str, **fields):
    """Update a job record in TinyDB."""
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    updated_ids = db.update(fields, Job.job_id == job_id)
    
    # ✅ FIXED: Log if job not found
    if not updated_ids:
        logger.warning(f"Job {job_id} not found in DB during update")


def run_full_pipeline(
    job_id: str,
    niche: str,
    company_context: str,
) -> None:
    """
    Background task: run the full 4-agent pipeline.

    Called by POST /api/v1/generate-ad.
    
    ✅ FIXED: Creates own DB connection (doesn't rely on Depends() context)
    """
    logger.info(f"[Job {job_id}] Starting full pipeline — niche='{niche}'")
    
    # ✅ FIXED: Create fresh DB connection inside the task
    db = _get_db()
    try:
        _update_job(db, job_id, status=JobStatus.RUNNING.value)

        pipeline = AdCrewPipeline(niche=niche, company_context=company_context)
        result = pipeline.run()

        _update_job(
            db,
            job_id,
            status=JobStatus.COMPLETED.value,
            result={
                "output_file": result.get("video_path", ""),
                "summary": f"Pipeline completed for niche '{niche}'",
                "artifacts": {
                    "crew_result": str(result.get("crew_result", "")),
                    "video_path": result.get("video_path", ""),
                },
            },
        )
        logger.info(f"[Job {job_id}] Full pipeline completed successfully")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        _update_job(
            db,
            job_id,
            status=JobStatus.FAILED.value,
            error=error_msg,
        )
        logger.error(f"[Job {job_id}] Pipeline failed: {e}")
    
    finally:
        # ✅ FIXED: Always close the DB connection
        db.close()


def run_analysis_only(
    job_id: str,
    ads_file_path: str,
) -> None:
    """
    Background task: run only the marketing analysis agent.

    Called by POST /api/v1/analyze-ads.
    
    ✅ FIXED: Creates own DB connection
    """
    logger.info(f"[Job {job_id}] Starting analysis on: {ads_file_path}")
    
    # ✅ FIXED: Create fresh DB connection
    db = _get_db()
    try:
        _update_job(db, job_id, status=JobStatus.RUNNING.value)

        pipeline = AdCrewPipeline()
        result = pipeline.run_analysis_only(ads_file_path)

        _update_job(
            db,
            job_id,
            status=JobStatus.COMPLETED.value,
            result={
                "output_file": ads_file_path,
                "summary": "Marketing analysis completed",
                "artifacts": {"crew_result": str(result.get("crew_result", ""))},
            },
        )
        logger.info(f"[Job {job_id}] Analysis completed")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        _update_job(db, job_id, status=JobStatus.FAILED.value, error=error_msg)
        logger.error(f"[Job {job_id}] Analysis failed: {e}")
    
    finally:
        # ✅ FIXED: Always close
        db.close()


def run_video_only(
    job_id: str,
    script_file_path: str,
) -> None:
    """
    Background task: run only the video production agent.

    Called by POST /api/v1/create-video.
    
    ✅ FIXED: Creates own DB connection
    """
    logger.info(f"[Job {job_id}] Starting video production from: {script_file_path}")
    
    # ✅ FIXED: Create fresh DB connection
    db = _get_db()
    try:
        _update_job(db, job_id, status=JobStatus.RUNNING.value)

        pipeline = AdCrewPipeline()
        result = pipeline.run_video_only(script_file_path)

        _update_job(
            db,
            job_id,
            status=JobStatus.COMPLETED.value,
            result={
                "output_file": result.get("video_path", ""),
                "summary": "Video production completed",
                "artifacts": {
                    "crew_result": str(result.get("crew_result", "")),
                    "video_path": result.get("video_path", ""),
                },
            },
        )
        logger.info(f"[Job {job_id}] Video production completed")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        _update_job(db, job_id, status=JobStatus.FAILED.value, error=error_msg)
        logger.error(f"[Job {job_id}] Video production failed: {e}")
    
    finally:
        # ✅ FIXED: Always close
        db.close()