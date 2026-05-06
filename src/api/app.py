# ═══════════════════════════════════
# FILE: src/api/app.py
# PURPOSE: FastAPI app factory
# ═══════════════════════════════════

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="CrowdWisdomTrading — AI Ads Pipeline",
        description=(
            "A backend API for generating high-converting trading ads "
            "using a 4-agent CrewAI pipeline: scrape → analyse → script → video."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — allow all for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="/api/v1")

    @app.on_event("startup")
    async def on_startup():
        settings.ensure_directories()
        logger.info("CrowdWisdomTrading API started")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "cwt-ads-agent"}

    return app
