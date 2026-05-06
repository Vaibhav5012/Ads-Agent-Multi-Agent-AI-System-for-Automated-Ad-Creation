# ═══════════════════════════════════
# FILE: src/tools/gdrive_tool.py
# PURPOSE: CrewAI Tool — read company documents from Google Drive
# ═══════════════════════════════════

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.retry_utils import retry_on_failure

logger = get_logger()


class GDriveInputSchema(BaseModel):
    """Input schema for the Google Drive reader tool."""

    folder_id: str = Field(
        default="",
        description="Google Drive folder ID. Defaults to env GDRIVE_FOLDER_ID.",
    )


class GDriveReaderTool(BaseTool):
    """Reads company documents from a Google Drive folder."""

    name: str = "Google Drive Reader"
    description: str = (
        "Reads company information documents (.txt, .md) from a specified "
        "Google Drive folder. Falls back to local company_data/ directory."
    )
    args_schema: type[BaseModel] = GDriveInputSchema

    def _run(self, folder_id: str = "") -> str:
        """Read company docs from GDrive; fall back to local files."""
        settings = get_settings()
        folder_id = folder_id or settings.gdrive_folder_id

        # Try Google Drive first
        if folder_id and Path(settings.gdrive_service_account_file).exists():
            try:
                return self._read_from_gdrive(folder_id, settings)
            except Exception as e:
                logger.warning(f"GDrive read failed ({e}), falling back to local files")

        # Fallback: read from local company_data directory
        return self._read_local_fallback(settings)

    @retry_on_failure(max_attempts=2)
    def _read_from_gdrive(self, folder_id: str, settings) -> str:
        """Authenticate and read files from Google Drive."""
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

        credentials = service_account.Credentials.from_service_account_file(
            settings.gdrive_service_account_file,
            scopes=SCOPES,
        )

        service = build("drive", "v3", credentials=credentials)

        # List files in the folder
        query = f"'{folder_id}' in parents and trashed = false"
        results = (
            service.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
        )
        files = results.get("files", [])
        logger.info(f"Found {len(files)} files in GDrive folder {folder_id}")

        combined_text = []
        for f in files:
            name = f["name"]
            mime = f.get("mimeType", "")

            # Only read text-based files
            if not any(name.endswith(ext) for ext in (".txt", ".md", ".csv")):
                # Try exporting Google Docs as text
                if "document" in mime:
                    request = service.files().export_media(
                        fileId=f["id"], mimeType="text/plain"
                    )
                else:
                    continue
            else:
                request = service.files().get_media(fileId=f["id"])

            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            content = buffer.getvalue().decode("utf-8", errors="replace")
            combined_text.append(f"--- {name} ---\n{content}\n")
            logger.info(f"Read GDrive file: {name} ({len(content)} chars)")

        if not combined_text:
            raise ValueError("No readable files found in GDrive folder")

        return "\n".join(combined_text)

    def _read_local_fallback(self, settings) -> str:
        """Read company data from local files."""
        company_dir = Path(settings.company_data_dir)
        combined = []

        if company_dir.exists():
            for fpath in sorted(company_dir.iterdir()):
                if fpath.suffix in (".md", ".txt", ".csv"):
                    content = fpath.read_text(encoding="utf-8")
                    combined.append(f"--- {fpath.name} ---\n{content}\n")
                    logger.info(f"Read local file: {fpath.name}")

        if not combined:
            logger.warning("No company data found — returning default description")
            return (
                "CrowdWisdomTrading is a trading education and signals platform. "
                "It offers daily live trading sessions, stock and options alerts "
                "powered by crowd wisdom (collective intelligence of 3,000+ members), "
                "and an active community. The platform boasts an 85% win rate on alerts. "
                "Website: crowdwisdomtrading.com"
            )

        return "\n".join(combined)
