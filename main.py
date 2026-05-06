# ═══════════════════════════════════
# FILE: main.py
# PURPOSE: Entry point — runs the full crew pipeline or starts the FastAPI server
# ═══════════════════════════════════

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()


def validate_env() -> bool:
    """Check that critical environment variables are set."""
    from src.config.settings import get_settings
    from src.utils.logger import get_logger

    logger = get_logger()
    settings = get_settings()

    warnings = []

    if not settings.openrouter_api_key:
        logger.error("OPENROUTER_API_KEY is not set — LLM calls will fail")
        return False

    if not settings.apify_api_token:
        warnings.append("APIFY_API_TOKEN not set — scraping will use mock data")
    if not settings.elevenlabs_api_key:
        warnings.append("ELEVENLABS_API_KEY not set — audio will be silent placeholders")
    if not settings.gdrive_folder_id:
        warnings.append("GDRIVE_FOLDER_ID not set — will use local company data fallback")

    for w in warnings:
        logger.warning(w)

    return True


def run_pipeline(niche: str) -> None:
    """Run the full 4-agent CrewAI pipeline."""
    from src.crew.ad_crew import AdCrewPipeline
    from src.utils.logger import get_logger

    logger = get_logger()
    logger.info(f"=== CrowdWisdomTrading Pipeline — niche: '{niche}' ===")

    pipeline = AdCrewPipeline(niche=niche)
    result = pipeline.run()

    logger.info("Pipeline result:")
    for key, value in result.items():
        logger.info(f"  {key}: {value}")

    logger.info("=== Pipeline complete ===")


def run_api(host: str, port: int) -> None:
    """Start the FastAPI server with Uvicorn."""
    import uvicorn
    from src.utils.logger import get_logger

    logger = get_logger()
    logger.info(f"Starting FastAPI server on {host}:{port}")
    logger.info(f"  Docs: http://{host}:{port}/docs")
    logger.info(f"  Health: http://{host}:{port}/health")

    uvicorn.run(
        "src.api.app:create_app",
        host=host,
        port=port,
        factory=True,
        reload=False,
        log_level="info",
    )


def main() -> None:
    """Parse arguments and dispatch to the appropriate mode."""
    parser = argparse.ArgumentParser(
        description="CrowdWisdomTrading — AI-Powered Ads Creation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python main.py --mode pipeline --niche "trading"
  python main.py --mode api --host 0.0.0.0 --port 8000
        """,
    )
    parser.add_argument(
        "--mode",
        choices=["pipeline", "api"],
        default="api",
        help="Run mode: 'pipeline' for direct execution, 'api' for REST server (default: api)",
    )
    parser.add_argument(
        "--niche",
        default="trading",
        help="Ad niche to target (default: trading)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port (default: 8000)",
    )

    args = parser.parse_args()

    # Validate environment
    if not validate_env():
        print("ERROR: Missing required environment variables. See .env.example")
        sys.exit(1)

    if args.mode == "pipeline":
        run_pipeline(args.niche)
    elif args.mode == "api":
        run_api(args.host, args.port)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
