# ═══════════════════════════════════
# FILE: src/tools/apify_tool.py
# PURPOSE: CrewAI Tool — scrape Meta Ad Library ads via Apify
# ═══════════════════════════════════

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import Any

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.models.ad_models import ScrapedAd
from src.utils.logger import get_logger
from src.utils.retry_utils import retry_on_failure

logger = get_logger()


class ApifyInputSchema(BaseModel):
    """Input schema for the Apify scraper tool."""

    search_query: str = Field(..., description="Search term for the Meta Ad Library (e.g. 'trading')")
    max_ads: int = Field(default=20, description="Maximum number of ads to scrape per query")


class ApifyScraperTool(BaseTool):
    """Scrapes Meta Ad Library for trading/finance ads using Apify."""

    name: str = "Meta Ads Scraper"
    description: str = (
        "Scrapes the Meta Ad Library via Apify to find high-performing "
        "trading and finance ads. Returns a list of structured ad objects."
    )
    args_schema: type[BaseModel] = ApifyInputSchema

    def _run(self, search_query: str, max_ads: int = 20) -> str:
        """Execute the Apify actor and return scraped ads as a JSON string."""
        settings = get_settings()

        if not settings.apify_api_token:
            logger.warning("APIFY_API_TOKEN not set — returning mock data")
            return self._mock_scrape(search_query)

        try:
            return self._real_scrape(search_query, max_ads, settings)
        except Exception as e:
            logger.error(f"Apify scrape failed: {e}")
            logger.info("Falling back to mock data")
            return self._mock_scrape(search_query)

    @retry_on_failure(max_attempts=3)
    def _real_scrape(self, search_query: str, max_ads: int, settings: Any) -> str:
        """Call the Apify actor with retry logic."""
        from apify_client import ApifyClient

        client = ApifyClient(settings.apify_api_token)

        # Calculate date 30 days ago
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

        run_input = {
            "searchTerms": [search_query],
            "countryCode": "US",
            "adActiveStatus": "ACTIVE",
            "adReachedCountries": ["US"],
            "maxItems": max_ads,
            "startDate": thirty_days_ago,
        }

        logger.info(f"Starting Apify actor for query: '{search_query}'")
        run = client.actor("apify/facebook-ads-scraper").call(run_input=run_input)

        # Collect results from the dataset
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        logger.info(f"Scraped {len(items)} raw ads for '{search_query}'")

        ads = []
        for item in items:
            ad = self._parse_ad_item(item, search_query)
            if ad:
                ads.append(ad)

        # Sort by engagement score descending
        ads.sort(key=lambda a: a.engagement_score, reverse=True)
        top_ads = ads[:max_ads]

        import json
        return json.dumps(
            [ad.model_dump(mode="json") for ad in top_ads],
            indent=2,
        )

    def _parse_ad_item(self, item: dict, query: str) -> ScrapedAd | None:
        """Parse a raw Apify result item into a ScrapedAd model."""
        try:
            ad_copy = item.get("adCopy", "") or item.get("body", "") or ""
            headline = item.get("title", "") or item.get("headline", "") or ""

            # Extract hook (first sentence)
            hook = ""
            if ad_copy:
                sentences = re.split(r"(?<=[.!?])\s+", ad_copy)
                hook = sentences[0] if sentences else ""

            # Compute engagement score heuristic
            score = self._compute_engagement_score(item, ad_copy)

            return ScrapedAd(
                ad_id=str(item.get("id", item.get("adArchiveID", "unknown"))),
                advertiser_name=item.get("pageName", "") or item.get("advertiser_name", ""),
                headline=headline,
                hook=hook,
                ad_copy=ad_copy,
                cta_text=item.get("ctaText", "") or item.get("cta", ""),
                media_url=item.get("imageUrl", "") or item.get("videoUrl", ""),
                start_date=item.get("startDate", "") or item.get("start_date", ""),
                platform=item.get("platform", "facebook"),
                engagement_score=score,
                niche_tags=self._infer_tags(ad_copy, headline, query),
            )
        except Exception as e:
            logger.warning(f"Failed to parse ad item: {e}")
            return None

    def _compute_engagement_score(self, item: dict, ad_copy: str) -> float:
        """Heuristic engagement score between 0.0 and 1.0."""
        score = 0.5  # Base score

        # Longer copy often correlates with higher engagement
        word_count = len(ad_copy.split())
        if word_count > 50:
            score += 0.1
        if word_count > 100:
            score += 0.1

        # Emotional language presence
        emotional_words = [
            "free", "limited", "exclusive", "proven", "guaranteed",
            "secret", "warning", "urgent", "now", "today",
            "don't miss", "last chance", "results", "profit",
        ]
        emotional_count = sum(
            1 for w in emotional_words if w.lower() in ad_copy.lower()
        )
        score += min(emotional_count * 0.03, 0.15)

        # Has CTA
        if item.get("ctaText") or item.get("cta"):
            score += 0.05

        # Has media
        if item.get("imageUrl") or item.get("videoUrl"):
            score += 0.05

        # Impressions / reach if available
        reach = item.get("estimatedReach", 0) or item.get("impressions", 0)
        if isinstance(reach, (int, float)) and reach > 10000:
            score += 0.1
        elif isinstance(reach, str) and "k" in reach.lower():
            score += 0.1

        return round(min(score, 1.0), 2)

    def _infer_tags(self, ad_copy: str, headline: str, query: str) -> list[str]:
        """Infer niche tags from ad content."""
        combined = f"{ad_copy} {headline}".lower()
        tags = set()
        tag_keywords = {
            "trading": "trading",
            "stock": "stock market",
            "options": "options trading",
            "crypto": "crypto",
            "forex": "forex",
            "investing": "investing",
            "day trad": "day trading",
            "swing": "swing trading",
            "bitcoin": "crypto",
            "financial freedom": "financial freedom",
            "passive income": "passive income",
        }
        for keyword, tag in tag_keywords.items():
            if keyword in combined:
                tags.add(tag)

        # Always include the query
        tags.add(query.lower())
        return sorted(tags)

    def _mock_scrape(self, query: str) -> str:
        """Return realistic mock ad data for development/testing."""
        import json

        mock_ads = [
            ScrapedAd(
                ad_id="meta_ad_mock_001",
                advertiser_name="TradeMaster Academy",
                headline="Stop Losing Money in the Stock Market",
                hook="What if I told you 90% of traders fail because of ONE mistake?",
                ad_copy=(
                    "What if I told you 90% of traders fail because of ONE mistake? "
                    "Most retail traders lose money because they trade on emotion, not data. "
                    "TradeMaster Academy teaches you the exact system used by professional "
                    "hedge fund managers. Join 5,000+ profitable traders who made the switch. "
                    "Limited spots available this month."
                ),
                cta_text="Start Your Free Trial",
                media_url="https://picsum.photos/1080/1920?random=1",
                start_date="2026-04-10",
                platform="facebook",
                engagement_score=0.92,
                niche_tags=["stock market", "trading education", "options"],
            ),
            ScrapedAd(
                ad_id="meta_ad_mock_002",
                advertiser_name="CryptoSignals Pro",
                headline="I Made $12,000 Last Month Trading Crypto Part-Time",
                hook="I quit my 9-5 after discovering this crypto strategy.",
                ad_copy=(
                    "I quit my 9-5 after discovering this crypto strategy. In just 3 months, "
                    "I went from losing money to making consistent profits every single week. "
                    "Our AI-powered signals tell you exactly when to buy and sell. No experience "
                    "needed. Join the free Telegram group and see the results yourself."
                ),
                cta_text="Join Free Telegram",
                media_url="https://picsum.photos/1080/1920?random=2",
                start_date="2026-04-15",
                platform="instagram",
                engagement_score=0.87,
                niche_tags=["crypto", "signals", "passive income"],
            ),
            ScrapedAd(
                ad_id="meta_ad_mock_003",
                advertiser_name="OptionsFlow Elite",
                headline="Warning: The Market Is About to Crash",
                hook="The last time this indicator flashed, the market dropped 30%.",
                ad_copy=(
                    "The last time this indicator flashed, the market dropped 30%. "
                    "Smart money is already positioning. Are you? Our options flow scanner "
                    "detects institutional trades BEFORE they move the market. Get real-time "
                    "alerts and protect your portfolio. First 100 members get 50% off."
                ),
                cta_text="Get Early Access",
                media_url="https://picsum.photos/1080/1920?random=3",
                start_date="2026-04-18",
                platform="facebook",
                engagement_score=0.95,
                niche_tags=["options trading", "market crash", "institutional flow"],
            ),
            ScrapedAd(
                ad_id="meta_ad_mock_004",
                advertiser_name="WealthPilot",
                headline="From $0 to $100K — My Trading Journey",
                hook="Two years ago I had nothing. Today I manage a six-figure portfolio.",
                ad_copy=(
                    "Two years ago I had nothing. Today I manage a six-figure portfolio. "
                    "The difference? A proven system that removes emotion from trading. "
                    "WealthPilot's AI scans 10,000 setups daily and only alerts you to the "
                    "highest-probability trades. Try it free for 14 days."
                ),
                cta_text="Start Free Trial",
                media_url="https://picsum.photos/1080/1920?random=4",
                start_date="2026-04-12",
                platform="facebook",
                engagement_score=0.89,
                niche_tags=["trading", "AI", "portfolio management"],
            ),
            ScrapedAd(
                ad_id="meta_ad_mock_005",
                advertiser_name="DayTrader Academy",
                headline="Wall Street Doesn't Want You to See This",
                hook="Wall Street doesn't want you to see this.",
                ad_copy=(
                    "Wall Street doesn't want you to see this. The same strategies "
                    "used by institutional traders are now available to retail investors. "
                    "Our members averaged 47% returns last year. Free masterclass reveals "
                    "the 3-step system. Register now before spots fill up."
                ),
                cta_text="Watch Free Masterclass",
                media_url="https://picsum.photos/1080/1920?random=5",
                start_date="2026-04-20",
                platform="instagram",
                engagement_score=0.91,
                niche_tags=["day trading", "institutional strategies", "education"],
            ),
        ]

        return json.dumps(
            [ad.model_dump(mode="json") for ad in mock_ads],
            indent=2,
        )
