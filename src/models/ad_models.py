# ═══════════════════════════════════
# FILE: src/models/ad_models.py
# PURPOSE: Pydantic models for scraped ads from Meta Ad Library
# ═══════════════════════════════════
"""
Example output (data/scraped_ads/example_ads.json):

[
  {
    "ad_id": "meta_ad_38291047",
    "advertiser_name": "TradeMaster Academy",
    "headline": "Stop Losing Money in the Stock Market",
    "hook": "What if I told you 90% of traders fail because of ONE mistake?",
    "ad_copy": "What if I told you 90% of traders fail because of ONE mistake? Most retail traders lose money because they trade on emotion, not data. TradeMaster Academy teaches you the exact system used by professional hedge fund managers. Join 5,000+ profitable traders who made the switch. Limited spots available this month.",
    "cta_text": "Start Your Free Trial",
    "media_url": "https://example.com/ad_image_38291047.jpg",
    "start_date": "2026-04-10",
    "platform": "facebook",
    "engagement_score": 0.92,
    "niche_tags": ["stock market", "trading education", "options"]
  },
  {
    "ad_id": "meta_ad_74920183",
    "advertiser_name": "CryptoSignals Pro",
    "headline": "I Made $12,000 Last Month Trading Crypto Part-Time",
    "hook": "I quit my 9-5 after discovering this crypto strategy.",
    "ad_copy": "I quit my 9-5 after discovering this crypto strategy. In just 3 months, I went from losing money to making consistent profits every single week. Our AI-powered signals tell you exactly when to buy and sell. No experience needed. Join the free Telegram group and see the results yourself.",
    "cta_text": "Join Free Telegram",
    "media_url": "https://example.com/ad_video_74920183.mp4",
    "start_date": "2026-04-15",
    "platform": "instagram",
    "engagement_score": 0.87,
    "niche_tags": ["crypto", "signals", "passive income"]
  },
  {
    "ad_id": "meta_ad_55018392",
    "advertiser_name": "OptionsFlow Elite",
    "headline": "Warning: The Market Is About to Crash",
    "hook": "The last time this indicator flashed, the market dropped 30%.",
    "ad_copy": "The last time this indicator flashed, the market dropped 30%. Smart money is already positioning. Are you? Our options flow scanner detects institutional trades BEFORE they move the market. Get real-time alerts and protect your portfolio. First 100 members get 50% off.",
    "cta_text": "Get Early Access",
    "media_url": "https://example.com/ad_image_55018392.jpg",
    "start_date": "2026-04-18",
    "platform": "facebook",
    "engagement_score": 0.95,
    "niche_tags": ["options trading", "market crash", "institutional flow"]
  }
]
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScrapedAd(BaseModel):
    """A single ad scraped from the Meta Ad Library."""

    ad_id: str = Field(..., description="Unique identifier for the ad")
    advertiser_name: str = Field(default="", description="Name of the advertiser")
    headline: str = Field(default="", description="Ad headline")
    hook: str = Field(default="", description="Opening hook — first sentence or attention-grabber")
    ad_copy: str = Field(default="", description="Full body text of the ad")
    cta_text: str = Field(default="", description="Call-to-action text")
    media_url: str = Field(default="", description="URL to the ad's image or video creative")
    start_date: str = Field(default="", description="Ad start date (YYYY-MM-DD)")
    platform: str = Field(default="facebook", description="Platform where the ad ran")
    engagement_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Heuristic engagement score between 0.0 and 1.0",
    )
    niche_tags: list[str] = Field(default_factory=list, description="Niche/category tags")


class AdCollection(BaseModel):
    """A ranked collection of scraped ads."""

    ads: list[ScrapedAd] = Field(default_factory=list, description="List of scraped ads")
    total_scraped: int = Field(default=0, description="Total raw ads scraped before filtering")
    query_terms: list[str] = Field(default_factory=list, description="Search queries used")
    scraped_at: str = Field(default="", description="UTC timestamp of scrape run")
    file_path: str = Field(default="", description="Path where collection was saved")
