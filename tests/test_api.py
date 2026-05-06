# ═══════════════════════════════════
# FILE: tests/test_api.py
# PURPOSE: Unit tests for FastAPI endpoints
# ═══════════════════════════════════

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_env():
    """Set required env vars and clear settings cache."""
    with patch.dict(os.environ, {
        "OPENROUTER_API_KEY": "test-key-for-api",
        "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
        "OPENROUTER_MODEL": "meta-llama/llama-3.3-70b-instruct:free",
        "APIFY_API_TOKEN": "",
        "ELEVENLABS_API_KEY": "",
    }):
        from src.config.settings import get_settings
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    from src.api.app import create_app
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, client):
        """GET /health should return 200 with status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cwt-ads-agent"


class TestGenerateAdEndpoint:
    """Tests for POST /api/v1/generate-ad."""

    def test_generate_ad_queues_job(self, client):
        """Should return a job_id with status 'queued'."""
        response = client.post(
            "/api/v1/generate-ad",
            json={"niche": "trading", "company_context": ""},
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

    def test_generate_ad_default_niche(self, client):
        """Should accept request with default niche."""
        response = client.post("/api/v1/generate-ad", json={})
        assert response.status_code == 200
        assert response.json()["status"] == "queued"


class TestAnalyzeAdsEndpoint:
    """Tests for POST /api/v1/analyze-ads."""

    def test_analyze_ads_queues_job(self, client):
        """Should queue an analysis job."""
        response = client.post(
            "/api/v1/analyze-ads",
            json={"ads_file_path": "data/scraped_ads/ads_latest.json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"

    def test_analyze_ads_requires_path(self, client):
        """Should fail without ads_file_path."""
        response = client.post("/api/v1/analyze-ads", json={})
        assert response.status_code == 422  # Validation error


class TestCreateVideoEndpoint:
    """Tests for POST /api/v1/create-video."""

    def test_create_video_queues_job(self, client):
        """Should queue a video creation job."""
        response = client.post(
            "/api/v1/create-video",
            json={"script_file_path": "data/scripts/script_latest.json"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "queued"


class TestStatusEndpoint:
    """Tests for GET /api/v1/status/{job_id}."""

    def test_status_of_queued_job(self, client):
        """After generating, status should be retrievable."""
        # Queue a job
        gen_response = client.post(
            "/api/v1/generate-ad",
            json={"niche": "crypto"},
        )
        job_id = gen_response.json()["job_id"]

        # Check status
        status_response = client.get(f"/api/v1/status/{job_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["job_id"] == job_id
        assert data["status"] in ("queued", "running", "completed", "failed")

    def test_status_nonexistent_job(self, client):
        """Should return 404 for a non-existent job."""
        response = client.get("/api/v1/status/nonexistent-uuid")
        assert response.status_code == 404


class TestJobsEndpoint:
    """Tests for GET /api/v1/jobs."""

    def test_list_jobs(self, client):
        """Should return a list of jobs."""
        # Queue a couple of jobs first
        client.post("/api/v1/generate-ad", json={"niche": "trading"})
        client.post("/api/v1/generate-ad", json={"niche": "crypto"})

        response = client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "jobs" in data
        assert data["total"] >= 2


class TestUploadCompanyData:
    """Tests for POST /api/v1/upload-company-data."""

    def test_upload_file(self, client):
        """Should upload a file to company_data/."""
        response = client.post(
            "/api/v1/upload-company-data",
            files={"file": ("test_info.md", b"# Test Company\nSome info here.", "text/markdown")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test_info.md"
        assert data["size_bytes"] > 0

        # Cleanup
        uploaded_path = Path(data["path"])
        if uploaded_path.exists():
            uploaded_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
