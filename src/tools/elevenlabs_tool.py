# ═══════════════════════════════════
# FILE: src/tools/elevenlabs_tool.py
# PURPOSE: CrewAI Tool — synthesize voiceover audio via ElevenLabs
# ═══════════════════════════════════

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.retry_utils import retry_on_failure

logger = get_logger()


class ElevenLabsInputSchema(BaseModel):
    """Input schema for the ElevenLabs TTS tool."""

    text: str = Field(..., description="Text to synthesize into speech")
    output_path: str = Field(..., description="File path to save the MP3 audio")
    voice_id: str = Field(default="", description="ElevenLabs voice ID override")


class ElevenLabsTTSTool(BaseTool):
    """Synthesizes speech audio from text using the ElevenLabs API."""

    name: str = "ElevenLabs Voice Synthesizer"
    description: str = (
        "Converts text to realistic speech audio using ElevenLabs TTS API. "
        "Saves the output as an MP3 file."
    )
    args_schema: type[BaseModel] = ElevenLabsInputSchema

    def _run(self, text: str, output_path: str, voice_id: str = "") -> str:
        """Synthesize text to speech and save as MP3."""
        settings = get_settings()
        voice_id = voice_id or settings.elevenlabs_voice_id
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if not settings.elevenlabs_api_key:
            logger.warning("ELEVENLABS_API_KEY not set — generating silent placeholder")
            return self._generate_silent_audio(text, output)

        try:
            return self._synthesize(text, output, voice_id, settings)
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            logger.info("Falling back to silent audio placeholder")
            return self._generate_silent_audio(text, output)

    @retry_on_failure(max_attempts=3)
    def _synthesize(self, text: str, output: Path, voice_id: str, settings) -> str:
        """Call the ElevenLabs API to synthesize speech."""
        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=settings.elevenlabs_api_key)

        logger.info(f"Synthesizing {len(text.split())} words → {output}")

        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=settings.elevenlabs_model_id,
            output_format="mp3_44100_128",
        )

        # Write audio bytes to file
        with open(output, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        logger.info(f"Audio saved → {output} ({output.stat().st_size} bytes)")
        return str(output.resolve())

    def _generate_silent_audio(self, text: str, output: Path) -> str:
        """Generate a silent audio file of approximate duration as a placeholder."""
        from src.utils.text_utils import estimate_duration

        duration = estimate_duration(text)
        logger.info(f"Generating {duration}s silent placeholder → {output}")

        try:
            # Use ffmpeg to generate a silent audio file
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"anullsrc=r=44100:cl=mono",
                    "-t", str(duration),
                    "-q:a", "9",
                    str(output),
                ],
                capture_output=True,
                check=True,
                timeout=30,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If ffmpeg isn't available, create a minimal valid MP3
            # (just write enough bytes to be a recognisable file)
            output.write_bytes(b"\xff\xfb\x90\x00" * max(1, int(duration * 100)))

        return str(output.resolve())

    @staticmethod
    def stitch_audio_files(audio_paths: list[str], output_path: str) -> str:
        """Concatenate multiple MP3 files into one using FFmpeg."""
        import tempfile

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Create a concat file list
        concat_file = output.parent / "concat_list.txt"
        with open(concat_file, "w") as f:
            for p in audio_paths:
                f.write(f"file '{Path(p).resolve()}'\n")

        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy",
                    str(output),
                ],
                capture_output=True,
                check=True,
                timeout=120,
            )
            logger.info(f"Stitched {len(audio_paths)} audio files → {output}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"FFmpeg concat failed ({e}), copying first file")
            if audio_paths:
                import shutil
                shutil.copy2(audio_paths[0], output)
        finally:
            concat_file.unlink(missing_ok=True)

        return str(output.resolve())
