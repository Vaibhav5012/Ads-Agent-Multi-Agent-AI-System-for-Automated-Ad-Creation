# ═══════════════════════════════════
# FILE: src/api/routes.py
# PURPOSE: All FastAPI route handlers
# ═══════════════════════════════════

from __future__ import annotations

import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse

from src.api.dependencies import get_db
from src.api.background_tasks import (
    run_full_pipeline,
    run_analysis_only,
    run_video_only,
)
from src.config.settings import get_settings
from src.models.job_models import (
    GenerateAdRequest,
    AnalyzeAdsRequest,
    CreateVideoRequest,
    JobResponse,
    JobDetailResponse,
    JobStatus,
)
from src.utils.logger import get_logger

logger = get_logger()
router = APIRouter()


# ── POST /generate-ad ──────────────────────────

@router.post("/generate-ad", response_model=JobResponse)
async def generate_ad(
    request: GenerateAdRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    """Queue a full 4-agent pipeline run."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    db.insert({
        "job_id": job_id,
        "job_type": "generate_ad",
        "status": JobStatus.QUEUED.value,
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "input_params": request.model_dump(),
    })

    background_tasks.add_task(
        run_full_pipeline, job_id, request.niche, request.company_context
    )
    logger.info(f"Queued full pipeline job: {job_id}")

    return JobResponse(job_id=job_id, status=JobStatus.QUEUED.value)


# ── POST /analyze-ads ─────────────────────────

@router.post("/analyze-ads", response_model=JobResponse)
async def analyze_ads(
    request: AnalyzeAdsRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    """Queue an analysis-only run (Agent 2) on existing scraped ads."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    db.insert({
        "job_id": job_id,
        "job_type": "analyze_ads",
        "status": JobStatus.QUEUED.value,
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "input_params": request.model_dump(),
    })

    background_tasks.add_task(
        run_analysis_only, job_id, request.ads_file_path
    )
    logger.info(f"Queued analysis job: {job_id}")

    return JobResponse(job_id=job_id, status=JobStatus.QUEUED.value)


# ── POST /create-video ────────────────────────

@router.post("/create-video", response_model=JobResponse)
async def create_video(
    request: CreateVideoRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    """Queue a video-only run (Agent 4) on an existing script."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    db.insert({
        "job_id": job_id,
        "job_type": "create_video",
        "status": JobStatus.QUEUED.value,
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "input_params": request.model_dump(),
    })

    background_tasks.add_task(
        run_video_only, job_id, request.script_file_path
    )
    logger.info(f"Queued video job: {job_id}")

    return JobResponse(job_id=job_id, status=JobStatus.QUEUED.value)


# ── GET /status/{job_id} ──────────────────────

@router.get("/status/{job_id}", response_model=JobDetailResponse)
async def get_job_status(job_id: str, db=Depends(get_db)):
    """Retrieve the current status of a job."""
    from tinydb import Query

    Job = Query()
    results = db.search(Job.job_id == job_id)

    if not results:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    record = results[0]
    return JobDetailResponse(
        job_id=record["job_id"],
        status=record["status"],
        result=record.get("result"),
        error=record.get("error"),
        created_at=record["created_at"],
        updated_at=record.get("updated_at", ""),
    )


# ── GET /jobs ─────────────────────────────────

@router.get("/jobs")
async def list_jobs(db=Depends(get_db)):
    """List all jobs."""
    all_jobs = db.all()
    return {
        "total": len(all_jobs),
        "jobs": all_jobs,
    }


# ── GET /download/{job_id} ────────────────────

@router.get("/download/{job_id}")
async def download_video(job_id: str, db=Depends(get_db)):
    """Download the final MP4 video for a completed job."""
    from tinydb import Query

    Job = Query()
    results = db.search(Job.job_id == job_id)

    if not results:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    record = results[0]

    if record["status"] != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed (status: {record['status']})",
        )

    result = record.get("result", {})
    video_path = ""

    if isinstance(result, dict):
        video_path = result.get("output_file", "") or result.get("video_path", "")

    if not video_path or not Path(video_path).exists():
        # Try to find the latest video in the videos directory
        settings = get_settings()
        videos = sorted(settings.videos_dir.glob("final_ad_*.mp4"), reverse=True)
        if videos:
            video_path = str(videos[0])
        else:
            raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=Path(video_path).name,
    )


# ── POST /upload-company-data ─────────────────

@router.post("/upload-company-data")
async def upload_company_data(file: UploadFile = File(...)):
    """Upload a company data file to the company_data/ directory."""
    settings = get_settings()
    company_dir = Path(settings.company_data_dir)
    company_dir.mkdir(parents=True, exist_ok=True)

    dest = company_dir / file.filename
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Uploaded company data: {dest}")
    return {
        "filename": file.filename,
        "path": str(dest),
        "size_bytes": len(content),
    }
