# ═══════════════════════════════════
# FILE: src/video/scene_builder.py
# PURPOSE: Converts AdScript scenes → Remotion props JSON
# ═══════════════════════════════════

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.script_models import AdScript, Scene
from src.utils.logger import get_logger

logger = get_logger()

FPS = 30


class SceneBuilder:
    """Converts an AdScript into Remotion-compatible props JSON."""

    def __init__(self, script: AdScript):
        self.script = script

    def build_props(
        self,
        audio_path: str = "",
        subtitle_data: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Build the complete props object that Remotion expects.

        Returns a dict with keys: scenes, subtitles, audioSrc.
        """
        scenes = []
        for scene in self.script.scenes:
            scenes.append(self._build_scene_props(scene))

        props = {
            "scenes": scenes,
            "subtitles": subtitle_data or [],
            "audioSrc": audio_path,
        }

        logger.info(f"Built Remotion props with {len(scenes)} scenes")
        return props

    def _build_scene_props(self, scene: Scene) -> dict[str, Any]:
        """Build props for a single Remotion scene component."""
        start_frame = int(scene.start_time_seconds * FPS)
        duration_frames = int(scene.duration_seconds * FPS)

        # Use Lorem Picsum for placeholder background images
        # Each scene gets a unique image based on scene number
        image_seed = scene.scene_number * 100
        image_url = f"https://picsum.photos/seed/{image_seed}/1080/1920"

        return {
            "sceneNumber": scene.scene_number,
            "sceneName": scene.scene_name,
            "startFrame": start_frame,
            "durationInFrames": duration_frames,
            "imageUrl": image_url,
            "visualDirection": scene.visual_direction,
            "voiceoverText": scene.voiceover,
            "subtitleText": scene.subtitle_text,
        }

    def save_props(
        self,
        output_path: Path | str,
        audio_path: str = "",
        subtitle_data: list[dict] | None = None,
    ) -> str:
        """Build and save props JSON to disk."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        props = self.build_props(audio_path, subtitle_data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(props, f, indent=2)

        logger.info(f"Saved Remotion props → {output_path}")
        return str(output_path.resolve())

    @staticmethod
    def total_frames(duration_seconds: int = 60, fps: int = FPS) -> int:
        """Calculate total frame count for a given duration."""
        return duration_seconds * fps
