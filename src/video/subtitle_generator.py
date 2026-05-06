# ═══════════════════════════════════
# FILE: src/video/subtitle_generator.py
# PURPOSE: Builds timed subtitle data from the ad script
# ═══════════════════════════════════

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.script_models import AdScript, Scene
from src.utils.text_utils import split_sentences, calculate_word_timings
from src.utils.logger import get_logger

logger = get_logger()

# Frames per second for Remotion
FPS = 30


class SubtitleGenerator:
    """Generates timed subtitle data from an AdScript."""

    def __init__(self, script: AdScript):
        self.script = script

    def generate(self) -> list[dict[str, Any]]:
        """
        Generate subtitle entries with frame-level timing.

        Returns a list of dicts:
            [
                {
                    "startFrame": int,
                    "endFrame": int,
                    "start_ms": int,
                    "end_ms": int,
                    "text": str,
                    "sceneNumber": int,
                },
                ...
            ]
        """
        subtitles: list[dict] = []

        for scene in self.script.scenes:
            scene_subs = self._generate_scene_subtitles(scene)
            subtitles.extend(scene_subs)

        logger.info(f"Generated {len(subtitles)} subtitle entries")
        return subtitles

    def _generate_scene_subtitles(self, scene: Scene) -> list[dict]:
        """Generate subtitle entries for a single scene."""
        text = scene.subtitle_text or scene.voiceover
        if not text:
            return []

        sentences = split_sentences(text)
        if not sentences:
            return []

        scene_start_ms = int(scene.start_time_seconds * 1000)
        scene_duration_ms = int(scene.duration_seconds * 1000)

        # Distribute time across sentences proportionally by word count
        total_words = sum(len(s.split()) for s in sentences)
        if total_words == 0:
            return []

        entries = []
        current_ms = scene_start_ms

        for sentence in sentences:
            word_count = len(sentence.split())
            sentence_duration_ms = int((word_count / total_words) * scene_duration_ms)
            end_ms = current_ms + sentence_duration_ms

            entries.append({
                "startFrame": self._ms_to_frames(current_ms),
                "endFrame": self._ms_to_frames(end_ms),
                "start_ms": current_ms,
                "end_ms": end_ms,
                "text": sentence,
                "sceneNumber": scene.scene_number,
            })

            current_ms = end_ms

        return entries

    def generate_srt(self) -> str:
        """Generate a standard .srt subtitle file string."""
        subtitles = self.generate()
        srt_lines = []

        for i, sub in enumerate(subtitles, 1):
            start = self._ms_to_srt_time(sub["start_ms"])
            end = self._ms_to_srt_time(sub["end_ms"])
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(sub["text"])
            srt_lines.append("")

        return "\n".join(srt_lines)

    def save(self, output_dir: Path | str) -> dict[str, str]:
        """Save subtitles as both JSON and SRT files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # JSON format (for Remotion)
        subtitles = self.generate()
        json_path = output_dir / "subtitles.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(subtitles, f, indent=2)
        logger.info(f"Saved subtitle JSON → {json_path}")

        # SRT format (standard)
        srt_content = self.generate_srt()
        srt_path = output_dir / "subtitles.srt"
        srt_path.write_text(srt_content, encoding="utf-8")
        logger.info(f"Saved SRT → {srt_path}")

        return {
            "json": str(json_path.resolve()),
            "srt": str(srt_path.resolve()),
        }

    @staticmethod
    def _ms_to_frames(ms: int) -> int:
        """Convert milliseconds to frame number at 30fps."""
        return int((ms / 1000) * FPS)

    @staticmethod
    def _ms_to_srt_time(ms: int) -> str:
        """Convert milliseconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = ms // 3_600_000
        minutes = (ms % 3_600_000) // 60_000
        seconds = (ms % 60_000) // 1000
        millis = ms % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
