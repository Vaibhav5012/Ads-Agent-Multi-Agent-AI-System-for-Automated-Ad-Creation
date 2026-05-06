# ═══════════════════════════════════
# FILE: src/video/remotion_orchestrator.py
# PURPOSE: Python wrapper that drives Remotion video rendering via subprocess
# ═══════════════════════════════════

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from src.config.settings import get_settings
from src.models.script_models import AdScript
from src.video.subtitle_generator import SubtitleGenerator
from src.video.scene_builder import SceneBuilder
from src.utils.file_utils import load_json, save_json, timestamped_path
from src.utils.logger import get_logger

logger = get_logger()


class RemotionOrchestrator:
    """
    Orchestrates the full video production pipeline:
      1. Load the ad script
      2. Generate subtitle data
      3. Build Remotion props JSON
      4. Invoke Remotion render via npx subprocess
    """

    def __init__(
        self,
        script_path: Optional[str] = None,
        audio_path: Optional[str] = None,
    ):
        self.settings = get_settings()
        self.script_path = script_path or str(
            self.settings.scripts_dir / "script_latest.json"
        )
        self.audio_path = audio_path or str(
            self.settings.videos_dir / "audio" / "final_voice.mp3"
        )
        self.remotion_dir = Path(self.settings.remotion_project_dir)
        self.props_path = self.remotion_dir / "public" / "props.json"

    def render(self) -> str:
        """
        Execute the full render pipeline and return the output video path.

        Returns the absolute path to the rendered MP4 file.
        """
        logger.info("Starting Remotion orchestration pipeline…")

        # Step 1: Load the ad script
        script = self._load_script()

        # Step 2: Generate subtitles
        subtitle_gen = SubtitleGenerator(script)
        subtitle_data = subtitle_gen.generate()
        subtitle_gen.save(self.settings.videos_dir)

        # Step 3: Build and save Remotion props
        scene_builder = SceneBuilder(script)
        self.props_path.parent.mkdir(parents=True, exist_ok=True)
        scene_builder.save_props(
            self.props_path,
            audio_path=self.audio_path,
            subtitle_data=subtitle_data,
        )

        # Step 4: Render via Remotion
        output_path = self._invoke_remotion_render()

        logger.info(f"Video render complete → {output_path}")
        return output_path

    def _load_script(self) -> AdScript:
        """Load and validate the ad script from JSON."""
        logger.info(f"Loading script from {self.script_path}")

        if not Path(self.script_path).exists():
            raise FileNotFoundError(f"Script not found: {self.script_path}")

        data = load_json(self.script_path)
        return AdScript(**data)

    def _invoke_remotion_render(self) -> str:
        """
        Call Remotion CLI to render the video.

        Runs: npx remotion render AdVideo --props=public/props.json output.mp4
        """
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_filename = f"final_ad_{ts}.mp4"
        output_path = self.settings.videos_dir / output_filename

        composition_id = self.settings.remotion_composition_id

        cmd = [
            "npx", "remotion", "render",
            composition_id,
            str(output_path.resolve()),
            f"--props={self.props_path.resolve()}",
            "--codec=h264",
        ]

        logger.info(f"Running Remotion render: {' '.join(cmd)}")

        if not self.remotion_dir.exists():
            logger.warning(
                f"Remotion project directory not found: {self.remotion_dir}. "
                "Skipping render — run 'cd remotion && npm install' first."
            )
            # Create a placeholder output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"")  # Empty placeholder
            return str(output_path.resolve())

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.remotion_dir.resolve()),
                capture_output=True,
                text=True,
                timeout=300,  # 5-minute timeout for render
            )

            if result.returncode != 0:
                logger.error(f"Remotion render failed:\n{result.stderr}")
                raise RuntimeError(f"Remotion render exited with code {result.returncode}")

            logger.info(f"Remotion stdout:\n{result.stdout[-500:]}")

        except FileNotFoundError:
            logger.warning("npx not found — Node.js may not be installed")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"")
        except subprocess.TimeoutExpired:
            logger.error("Remotion render timed out after 5 minutes")
            raise

        return str(output_path.resolve())

    def prepare_only(self) -> dict[str, str]:
        """
        Prepare all assets without rendering — useful for debugging.

        Returns paths to generated subtitle and props files.
        """
        script = self._load_script()

        subtitle_gen = SubtitleGenerator(script)
        subtitle_paths = subtitle_gen.save(self.settings.videos_dir)

        scene_builder = SceneBuilder(script)
        self.props_path.parent.mkdir(parents=True, exist_ok=True)
        subtitle_data = subtitle_gen.generate()
        props_path = scene_builder.save_props(
            self.props_path,
            audio_path=self.audio_path,
            subtitle_data=subtitle_data,
        )

        return {
            "subtitles_json": subtitle_paths["json"],
            "subtitles_srt": subtitle_paths["srt"],
            "props_json": props_path,
        }
