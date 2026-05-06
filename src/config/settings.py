# ═══════════════════════════════════
# FILE: src/config/settings.py
# PURPOSE: Pydantic BaseSettings — all environment variables in one place
# ═══════════════════════════════════

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application settings loaded from .env / environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── OpenRouter (LLM) ──────────────────────────
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter base URL",
    )
    openrouter_model: str = Field(
        default="meta-llama/llama-3.3-70b-instruct:free",
        description="LLM model identifier on OpenRouter",
    )

    # ── Apify ─────────────────────────────────────
    apify_api_token: str = Field(default="", description="Apify API token")

    # ── ElevenLabs ────────────────────────────────
    elevenlabs_api_key: str = Field(default="", description="ElevenLabs API key")
    elevenlabs_voice_id: str = Field(
        default="21m00Tcm4TlvDq8ikWAM",
        description="ElevenLabs voice ID",
    )
    elevenlabs_model_id: str = Field(
        default="eleven_monolingual_v1",
        description="ElevenLabs TTS model",
    )

    # ── Google Drive ──────────────────────────────
    gdrive_folder_id: str = Field(default="", description="Google Drive folder ID")
    gdrive_service_account_file: str = Field(
        default="credentials/service_account.json",
        description="Path to GDrive service-account JSON",
    )

    # ── FastAPI ───────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="API listen host")
    api_port: int = Field(default=8000, description="API listen port")
    api_workers: int = Field(default=1, description="Uvicorn workers")

    # ── Remotion ──────────────────────────────────
    remotion_project_dir: str = Field(default="remotion", description="Remotion project path")
    remotion_composition_id: str = Field(default="AdVideo", description="Remotion composition ID")

    # ── General ───────────────────────────────────
    log_level: str = Field(default="INFO", description="Logging level")
    data_dir: str = Field(default="data", description="Root data directory")
    company_data_dir: str = Field(default="company_data", description="Company data directory")

    # ── Derived paths ─────────────────────────────
    @property
    def scraped_ads_dir(self) -> Path:
        return Path(self.data_dir) / "scraped_ads"

    @property
    def analysis_dir(self) -> Path:
        return Path(self.data_dir) / "analysis"

    @property
    def scripts_dir(self) -> Path:
        return Path(self.data_dir) / "scripts"

    @property
    def videos_dir(self) -> Path:
        return Path(self.data_dir) / "videos"

    @property
    def jobs_db_path(self) -> Path:
        return Path(self.data_dir) / "jobs.json"

    def ensure_directories(self) -> None:
        """Create all required data directories if they don't exist."""
        for d in [
            self.scraped_ads_dir,
            self.analysis_dir,
            self.scripts_dir,
            self.videos_dir,
            self.videos_dir / "audio",
            Path(self.company_data_dir),
        ]:
            d.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    s = Settings()
    s.ensure_directories()
    return s


# Module-level singleton — importable as `from src.config.settings import settings`
settings = get_settings()
