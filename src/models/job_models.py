# ═══════════════════════════════════
# FILE: src/models/job_models.py
# PURPOSE: Pydantic models for API job tracking
# ═══════════════════════════════════

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobStatus(str, enum.Enum):
    """Possible states for a background job."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResult(BaseModel):
    """The result payload returned when a job completes."""

    output_file: str = Field(default="", description="Path to the output file")
    summary: str = Field(default="", description="Human-readable summary")
    artifacts: dict[str, str] = Field(
        default_factory=dict,
        description="Map of artifact names to file paths",
    )


class JobRecord(BaseModel):
    """A single job record stored in TinyDB."""

    job_id: str = Field(..., description="UUID of the job")
    job_type: str = Field(default="generate_ad", description="Type of job")
    status: JobStatus = Field(default=JobStatus.QUEUED, description="Current status")
    result: Optional[JobResult] = Field(default=None, description="Result on completion")
    error: Optional[str] = Field(default=None, description="Error message on failure")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of job creation",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of last update",
    )
    input_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters for the job",
    )


# ── Request / Response models for FastAPI ─────

class GenerateAdRequest(BaseModel):
    """POST /api/v1/generate-ad request body."""

    niche: str = Field(default="trading", description="Ad niche to target")
    company_context: str = Field(
        default="",
        description="Optional company context override",
    )


class AnalyzeAdsRequest(BaseModel):
    """POST /api/v1/analyze-ads request body."""

    ads_file_path: str = Field(..., description="Path to scraped ads JSON")


class CreateVideoRequest(BaseModel):
    """POST /api/v1/create-video request body."""

    script_file_path: str = Field(..., description="Path to script JSON")


class JobResponse(BaseModel):
    """Minimal job response returned immediately after queueing."""

    job_id: str
    status: str


class JobDetailResponse(BaseModel):
    """Full job detail response for GET /status/{job_id}."""

    job_id: str
    status: str
    result: Optional[JobResult] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str = ""
