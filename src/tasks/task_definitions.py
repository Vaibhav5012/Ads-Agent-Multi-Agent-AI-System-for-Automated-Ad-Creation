# ═══════════════════════════════════
# FILE: src/tasks/task_definitions.py
# PURPOSE: All CrewAI Task objects — one per agent
# ═══════════════════════════════════

from __future__ import annotations

import json
from textwrap import dedent

from crewai import Agent, Task

from src.config.settings import get_settings
from src.models.ad_models import ScrapedAd
from src.models.analysis_models import MarketingAnalysis
from src.models.script_models import AdScript, Scene


def create_ad_search_task(agent: Agent, niche: str = "trading") -> Task:
    """
    Task 1 — Scrape & rank the top 10 trading/finance ads.

    The agent uses the ApifyScraperTool to search the Meta Ad Library
    with multiple queries, scores the ads, and saves the top 10.
    """
    settings = get_settings()

    search_queries = [
        "trading", "stock market", "options trading",
        "crypto investing", "financial freedom", "day trading",
    ]

    return Task(
        description=dedent(f"""\
            You are tasked with finding the **top 10 highest-performing trading/finance ads**
            from the Meta Ad Library that were active in the last 30 days.

            STEPS:
            1. Use the "Meta Ads Scraper" tool to search for ads. Run the tool with the 
               search query "{niche}" and max_ads=20.
            2. The tool will return a JSON string of scraped ads.
            3. Parse the returned ads and evaluate each one.
            4. Score each ad by: engagement signals, copy length, emotional language,
               and overall quality.
            5. Select the top 10 ads with the highest scores.
            6. Use the "File IO" tool to save the top 10 ads as JSON to the file path:
               "{settings.scraped_ads_dir}/ads_latest.json"
               Pass the JSON string as the "data" parameter and the path as "file_path".
            7. Return the file path where you saved the ads.

            Additional search queries to consider: {json.dumps(search_queries)}

            The output should be the FILE PATH where the ads were saved, nothing else.
        """),
        expected_output=(
            "The absolute file path to the saved JSON file containing "
            "the top 10 ranked ads (e.g., data/scraped_ads/ads_latest.json)"
        ),
        agent=agent,
    )


def create_marketing_analysis_task(agent: Agent) -> Task:
    """
    Task 2 — Extract marketing intelligence from the scraped ads.

    The agent reads the scraped ads JSON, analyses the marketing psychology,
    and produces a structured MarketingAnalysis output.
    """
    settings = get_settings()

    # Build the schema description for the prompt
    schema_json = json.dumps(MarketingAnalysis.model_json_schema(), indent=2)

    analysis_prompt = dedent("""\
        You are a world-class direct response marketing analyst specialising
        in financial products, trading education, and wealth-building offers.

        You have been given ads scraped from the Meta Ad Library in the
        trading/finance niche. Your job is to reverse-engineer exactly WHY
        these ads perform well.

        Analyse every ad and extract:

        1. PAIN POINTS: The top 5 specific financial or emotional frustrations
           that these ads address (e.g., "losing money on bad trades",
           "missing out on market moves", "feeling left behind financially").
           Be specific, not generic.

        2. WINNING HOOKS: The 5 most compelling opening lines. For each,
           explain in 1 sentence WHY it grabs attention.

        3. EMOTIONAL TRIGGERS: List all psychological levers used across all
           ads (FOMO, aspiration, fear of loss, social proof, authority, etc.)

        4. URGENCY TACTICS: Specific language used to create urgency or scarcity.

        5. PERSUASION PATTERNS: The narrative structures used (problem-agitate-solve,
           before-after, us-vs-them, etc.)

        6. CTA ANALYSIS: What calls-to-action are used, which is most compelling
           and why.

        7. AUDIENCE PROFILE: Based on the ad language, describe exactly who
           these ads are targeting (age, income level, experience, psychology).

        8. TOP PERFORMING AD SUMMARY: Brief recap of the single best ad.
    """)

    return Task(
        description=dedent(f"""\
            You must analyse the scraped ads and extract marketing intelligence.

            STEPS:
            1. Use the "File IO" tool to load the ads from the file path provided
               by the previous task. The path should be something like
               "{settings.scraped_ads_dir}/ads_latest.json".
               Call the tool with file_path=<the path> and data="" (empty string to load).
            2. Read and understand every ad in the collection.
            3. Apply the following analysis framework:

            {analysis_prompt}

            4. Structure your analysis as a JSON object with these exact keys:
               - pain_points: list of 5 strings
               - winning_hooks: list of 5 objects with "hook" and "why_it_works" keys
               - emotional_triggers: list of strings
               - urgency_tactics: list of strings
               - persuasion_patterns: list of strings
               - cta_analysis: object with "common_ctas" (list) and "best_cta" (string)
               - audience_profile: string
               - top_performing_ad_summary: string
               - analyzed_at: current UTC timestamp string

            5. Use the "File IO" tool to save the analysis JSON to:
               "{settings.analysis_dir}/analysis_latest.json"
            6. Return the file path where the analysis was saved.
        """),
        expected_output=(
            "The absolute file path to the saved marketing analysis JSON "
            "(e.g., data/analysis/analysis_latest.json)"
        ),
        agent=agent,
    )


def create_script_generation_task(agent: Agent) -> Task:
    """
    Task 3 — Generate a 60-second ad script for CrowdWisdomTrading.

    The agent reads the marketing analysis, loads company data,
    and produces a structured 6-scene AdScript.
    """
    settings = get_settings()
    schema_json = json.dumps(AdScript.model_json_schema(), indent=2)

    script_prompt = dedent("""\
        You are an elite short-form video ad copywriter. You create 60-second
        scripts that stop the scroll, trigger emotion, and convert cold traffic.

        You are writing an ad for CrowdWisdomTrading (crowdwisdomtrading.com).

        STRICT REQUIREMENTS:
        - Total voiceover words: 140-160 words (60 seconds at 2.5 words/second)
        - Scene 1 hook: max 8 words, must be a question or shocking statement
        - Must use at least 2 pain points from the analysis
        - Must reference the company's unique value (crowd wisdom, collective intelligence)
        - CTA must include the URL and a specific number (e.g., "Join 3,000+ traders at CrowdWisdomTrading.com")
        - Tone: confident, human, urgent — like a friend giving advice, not a salesman
        - Style: TikTok/Instagram Reels — punchy sentences, short paragraphs

        SCRIPT STRUCTURE (exactly 6 scenes):
        Scene 1 — Hook (0-5s): Shocking question or bold statement
        Scene 2 — Pain Point (5-15s): Address a specific frustration
        Scene 3 — Agitation (15-25s): Amplify the pain, make it urgent
        Scene 4 — Solution Reveal (25-40s): Introduce CrowdWisdomTrading
        Scene 5 — Social Proof (40-50s): Numbers, testimonials, results
        Scene 6 — CTA (50-60s): Clear, specific call to action
    """)

    return Task(
        description=dedent(f"""\
            Generate a 60-second video ad script for CrowdWisdomTrading.

            STEPS:
            1. Use the "File IO" tool to load the marketing analysis from:
               "{settings.analysis_dir}/analysis_latest.json"
               (data="" to load).
            2. Use the "Google Drive Reader" tool to get company information.
               Pass folder_id="" to use the default.
            3. Study the pain points, hooks, and emotional triggers from the analysis.
            4. Apply this creative brief:

            {script_prompt}

            5. Create a JSON object with this structure:
               {{
                 "title": "Script title",
                 "total_duration_seconds": 60,
                 "total_word_count": <count>,
                 "scenes": [
                   {{
                     "scene_number": 1,
                     "scene_name": "Hook",
                     "start_time_seconds": 0,
                     "end_time_seconds": 5,
                     "visual_direction": "Description of what viewer sees",
                     "voiceover": "Spoken words",
                     "subtitle_text": "On-screen text",
                     "duration_seconds": 5
                   }},
                   ... (6 scenes total)
                 ],
                 "voiceover_segments": [...],
                 "metadata": {{
                   "company_name": "CrowdWisdomTrading",
                   "company_url": "crowdwisdomtrading.com",
                   "target_platform": "tiktok",
                   "tone": "confident, urgent, human",
                   "generated_at": "<timestamp>"
                 }}
               }}
            6. Save the script JSON using "File IO" to:
               "{settings.scripts_dir}/script_latest.json"
            7. Return the file path.
        """),
        expected_output=(
            "The absolute file path to the saved script JSON "
            "(e.g., data/scripts/script_latest.json)"
        ),
        agent=agent,
    )


def create_video_production_task(agent: Agent) -> Task:
    """
    Task 4 — Produce the final 60-second MP4 video.

    The agent reads the script, synthesizes voiceover audio for each scene,
    generates subtitles, and renders the video via Remotion.
    """
    settings = get_settings()

    return Task(
        description=dedent(f"""\
            Produce a complete 60-second video from the ad script.

            STEPS:
            1. Use the "File IO" tool to load the script from:
               "{settings.scripts_dir}/script_latest.json"
               (data="" to load).

            2. VOICE SYNTHESIS — For each scene in the script:
               a. Extract the voiceover text
               b. Use the "ElevenLabs Voice Synthesizer" tool to generate audio:
                  - text: the scene's voiceover text
                  - output_path: "{settings.videos_dir}/audio/scene_<N>.mp3"
                  - voice_id: "" (use default)
               c. Note the file path of each generated audio file

            3. After generating all scene audio files, report the list of
               audio file paths and confirm all were created.

            4. SUBTITLE GENERATION:
               - For each scene, calculate word-level timing based on the
                 scene duration and number of words.
               - Create a subtitle data structure with start_ms, end_ms, and text
                 for each subtitle chunk.

            5. Save a summary of all produced assets (audio paths, subtitle data)
               using "File IO" to:
               "{settings.videos_dir}/production_manifest.json"

            6. Return the path to the production manifest as the final output.

            NOTE: The Remotion video render will be handled by the orchestration
            layer after this task completes. Focus on generating the audio and
            subtitle assets.
        """),
        expected_output=(
            "The file path to the production manifest JSON containing "
            "all audio paths and subtitle timing data "
            "(e.g., data/videos/production_manifest.json)"
        ),
        agent=agent,
    )
