# ═══════════════════════════════════
# FILE: src/models/script_models.py
# PURPOSE: Pydantic models for the 60-second ad script
# ═══════════════════════════════════
"""
Example output (data/scripts/example_script.json):

{
  "title": "CrowdWisdomTrading — Stop Trading Alone",
  "total_duration_seconds": 60,
  "total_word_count": 148,
  "scenes": [
    {
      "scene_number": 1,
      "scene_name": "Hook",
      "start_time_seconds": 0,
      "end_time_seconds": 5,
      "visual_direction": "Close-up of a phone screen showing a portfolio down 40%. Red numbers filling the screen. Camera slowly zooms out to reveal a stressed person at their desk.",
      "voiceover": "Are you tired of losing money trading alone?",
      "subtitle_text": "Are you tired of losing money trading alone?",
      "duration_seconds": 5
    },
    {
      "scene_number": 2,
      "scene_name": "Pain Point",
      "start_time_seconds": 5,
      "end_time_seconds": 15,
      "visual_direction": "Split screen: left side shows Reddit forums and conflicting YouTube advice. Right side shows a confused trader surrounded by multiple monitors with charts.",
      "voiceover": "Every day, thousands of retail traders lose money because they're following random advice from strangers on the internet. No system. No edge. Just hoping for the best.",
      "subtitle_text": "Every day, thousands of retail traders lose money following random advice. No system. No edge.",
      "duration_seconds": 10
    },
    {
      "scene_number": 3,
      "scene_name": "Agitation",
      "start_time_seconds": 15,
      "end_time_seconds": 25,
      "visual_direction": "Montage of market crash headlines, red candlestick charts crashing, notification sounds of stop-losses being hit.",
      "voiceover": "While you second-guess every trade, the smart money is already positioned. They have teams, data, and systems. You have a phone and a prayer.",
      "subtitle_text": "Smart money is already positioned. They have teams and data. You have a phone and a prayer.",
      "duration_seconds": 10
    },
    {
      "scene_number": 4,
      "scene_name": "Solution Reveal",
      "start_time_seconds": 25,
      "end_time_seconds": 40,
      "visual_direction": "Bright transition to CrowdWisdomTrading platform. Show live trading room with chat active, green profit notifications popping up, members celebrating wins.",
      "voiceover": "What if you could trade with the collective intelligence of three thousand successful traders? CrowdWisdomTrading gives you daily live sessions, real-time alerts with an eighty-five percent win rate, and a community that actually helps you win.",
      "subtitle_text": "Trade with 3,000+ successful traders. Live sessions. 85% win rate alerts. A community that helps you win.",
      "duration_seconds": 15
    },
    {
      "scene_number": 5,
      "scene_name": "Social Proof",
      "start_time_seconds": 40,
      "end_time_seconds": 50,
      "visual_direction": "Scrolling testimonials from real members. Screenshots of profit notifications. Counter animating from 0 to 3,000+ members.",
      "voiceover": "Over three thousand traders have already made the switch. Members like Jake who turned five hundred dollars into ten thousand in his first month. This isn't luck — it's crowd wisdom.",
      "subtitle_text": "3,000+ traders made the switch. Jake turned $500 into $10K in month one. This is crowd wisdom.",
      "duration_seconds": 10
    },
    {
      "scene_number": 6,
      "scene_name": "CTA",
      "start_time_seconds": 50,
      "end_time_seconds": 60,
      "visual_direction": "CrowdWisdomTrading logo with URL. Countdown timer showing limited spots. Green 'Join Now' button pulsing.",
      "voiceover": "Stop trading alone. Join three thousand plus winning traders at CrowdWisdomTrading dot com. Your first week is free. But spots are limited — don't miss out.",
      "subtitle_text": "Join 3,000+ traders at CrowdWisdomTrading.com — First week FREE. Spots are limited!",
      "duration_seconds": 10
    }
  ],
  "voiceover_segments": [
    {
      "scene_number": 1,
      "text": "Are you tired of losing money trading alone?",
      "start_seconds": 0.0,
      "end_seconds": 5.0,
      "word_count": 9
    },
    {
      "scene_number": 2,
      "text": "Every day, thousands of retail traders lose money because they're following random advice from strangers on the internet. No system. No edge. Just hoping for the best.",
      "start_seconds": 5.0,
      "end_seconds": 15.0,
      "word_count": 30
    }
  ],
  "metadata": {
    "company_name": "CrowdWisdomTrading",
    "company_url": "crowdwisdomtrading.com",
    "target_platform": "tiktok",
    "tone": "confident, urgent, human",
    "generated_at": "2026-05-06T03:00:00Z"
  }
}
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Scene(BaseModel):
    """A single scene in the 60-second ad script."""

    scene_number: int = Field(..., description="Scene number (1-6)")
    scene_name: str = Field(..., description="Scene label (Hook, Pain Point, etc.)")
    start_time_seconds: float = Field(..., description="Scene start time in seconds")
    end_time_seconds: float = Field(..., description="Scene end time in seconds")
    visual_direction: str = Field(..., description="Direction for what the viewer sees")
    voiceover: str = Field(..., description="Spoken words for this scene")
    subtitle_text: str = Field(..., description="On-screen subtitle text")
    duration_seconds: float = Field(..., description="Scene duration in seconds")


class VoiceoverSegment(BaseModel):
    """A voiceover segment mapped to a scene."""

    scene_number: int = Field(..., description="Which scene this belongs to")
    text: str = Field(..., description="Voiceover text for the segment")
    start_seconds: float = Field(default=0.0, description="Start time in seconds")
    end_seconds: float = Field(default=0.0, description="End time in seconds")
    word_count: int = Field(default=0, description="Number of words")


class ScriptMetadata(BaseModel):
    """Metadata about the generated script."""

    company_name: str = Field(default="CrowdWisdomTrading")
    company_url: str = Field(default="crowdwisdomtrading.com")
    target_platform: str = Field(default="tiktok")
    tone: str = Field(default="confident, urgent, human")
    generated_at: str = Field(default="")


class AdScript(BaseModel):
    """Complete 60-second ad script with all 6 scenes."""

    title: str = Field(default="", description="Script title")
    total_duration_seconds: int = Field(default=60, description="Total duration")
    total_word_count: int = Field(default=0, description="Total voiceover words")
    scenes: list[Scene] = Field(default_factory=list, description="Ordered list of 6 scenes")
    voiceover_segments: list[VoiceoverSegment] = Field(
        default_factory=list,
        description="Voiceover segments per scene",
    )
    metadata: ScriptMetadata = Field(
        default_factory=ScriptMetadata,
        description="Script metadata",
    )
