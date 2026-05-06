# ═══════════════════════════════════
# FILE: src/models/analysis_models.py
# PURPOSE: Pydantic models for marketing analysis output
# ═══════════════════════════════════
"""
Example output (data/analysis/example_analysis.json):

{
  "pain_points": [
    "Losing money on bad trades due to emotional decision-making",
    "Missing out on market moves and feeling left behind",
    "Overwhelmed by conflicting trading information online",
    "Fear of another market crash wiping out savings",
    "Frustration with slow, inconsistent returns from traditional investing"
  ],
  "winning_hooks": [
    {
      "hook": "What if I told you 90% of traders fail because of ONE mistake?",
      "why_it_works": "Uses a specific statistic and curiosity gap — the reader must know what the 'one mistake' is."
    },
    {
      "hook": "I quit my 9-5 after discovering this crypto strategy.",
      "why_it_works": "Aspirational identity shift — speaks to the dream of financial freedom from employment."
    },
    {
      "hook": "The last time this indicator flashed, the market dropped 30%.",
      "why_it_works": "Fear-driven urgency combined with insider knowledge positioning."
    },
    {
      "hook": "Wall Street doesn't want you to see this.",
      "why_it_works": "Us-vs-them framing creates conspiracy-like intrigue and anti-establishment appeal."
    },
    {
      "hook": "I turned $500 into $15,000 in 30 days.",
      "why_it_works": "Specific numbers create credibility and activate greed/aspiration triggers."
    }
  ],
  "emotional_triggers": [
    "FOMO (fear of missing out on profitable trades)",
    "Aspiration (dream of financial freedom and quitting day job)",
    "Fear of loss (market crash, losing savings)",
    "Social proof (thousands of members, testimonials)",
    "Authority (hedge fund strategies, institutional data)",
    "Urgency (limited spots, prices going up)"
  ],
  "urgency_tactics": [
    "Limited spots available this month",
    "First 100 members get 50% off",
    "Price increases at midnight",
    "This opportunity won't last",
    "Join before the next market move"
  ],
  "persuasion_patterns": [
    "Problem-Agitate-Solve: identify pain → amplify fear → present solution",
    "Before-After: show life before vs. after using the product",
    "Us-vs-Them: retail traders vs. Wall Street / institutions",
    "Social Proof Cascade: member count → testimonials → results",
    "Scarcity Close: limited access creates urgency to act now"
  ],
  "cta_analysis": {
    "common_ctas": [
      "Start Your Free Trial",
      "Join Free Telegram",
      "Get Early Access",
      "Claim Your Spot",
      "Watch the Free Training"
    ],
    "best_cta": "Get Early Access — combines exclusivity with low commitment, making the action feel privileged rather than salesy."
  },
  "audience_profile": "Males aged 25-45, middle income ($40K-$100K), with some trading experience but inconsistent results. Frustrated with losing money, seeking a 'system' or 'edge'. Consumes financial content on YouTube and social media. Aspires to replace employment income with trading profits. Risk-tolerant but emotionally reactive to losses.",
  "top_performing_ad_summary": "OptionsFlow Elite's 'Warning: The Market Is About to Crash' ad scored highest (0.95) by combining fear of loss with insider positioning. The hook leverages a specific historical reference, the body builds authority through institutional flow data, and the scarcity CTA (first 100 members) creates immediate urgency.",
  "analyzed_at": "2026-05-06T03:00:00Z"
}
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PainPoint(BaseModel):
    """A specific financial or emotional pain point."""

    description: str = Field(..., description="Description of the pain point")
    frequency: int = Field(default=1, description="How many ads reference this pain point")


class Hook(BaseModel):
    """An opening hook with analysis of why it works."""

    hook: str = Field(..., description="The opening hook text")
    why_it_works: str = Field(..., description="One-sentence explanation of effectiveness")


class CTAAnalysis(BaseModel):
    """Breakdown of calls-to-action from the ads."""

    common_ctas: list[str] = Field(default_factory=list, description="Commonly used CTAs")
    best_cta: str = Field(default="", description="The most effective CTA and why")


class MarketingAnalysis(BaseModel):
    """Complete marketing intelligence extracted from competitor ads."""

    pain_points: list[str] = Field(
        default_factory=list,
        description="Top 5 specific financial/emotional pain points",
    )
    winning_hooks: list[dict] = Field(
        default_factory=list,
        description="Top 5 hooks with {hook, why_it_works}",
    )
    emotional_triggers: list[str] = Field(
        default_factory=list,
        description="Psychological levers used across ads",
    )
    urgency_tactics: list[str] = Field(
        default_factory=list,
        description="Urgency/scarcity language examples",
    )
    persuasion_patterns: list[str] = Field(
        default_factory=list,
        description="Narrative structures used",
    )
    cta_analysis: dict = Field(
        default_factory=dict,
        description="CTA breakdown: {common_ctas, best_cta}",
    )
    audience_profile: str = Field(
        default="",
        description="Inferred target audience description",
    )
    top_performing_ad_summary: str = Field(
        default="",
        description="Brief recap of the single best ad",
    )
    analyzed_at: str = Field(default="", description="UTC timestamp of analysis")
