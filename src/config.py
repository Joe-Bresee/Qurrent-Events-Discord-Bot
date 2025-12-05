"""Configuration management for the Qurrent Events Discord Bot."""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


@dataclass
class BotConfig:
    """Configuration settings for the Discord bot."""

    # Discord settings
    discord_token: str = ""
    news_channel_id: int = 0

    # YouTube channels to monitor (channel IDs for quantum computing content)
    youtube_channels: list[str] = field(default_factory=list)

    # News RSS feeds for quantum computing
    news_feeds: list[str] = field(default_factory=list)

    # Update intervals (in seconds)
    youtube_check_interval: int = 3600  # 1 hour
    news_check_interval: int = 1800  # 30 minutes

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        # Parse YouTube channels from comma-separated string
        youtube_channels_str = os.getenv("YOUTUBE_CHANNELS", "")
        youtube_channels = (
            [ch.strip() for ch in youtube_channels_str.split(",") if ch.strip()]
            if youtube_channels_str
            else cls._get_default_youtube_channels()
        )

        # Parse news feeds from comma-separated string
        news_feeds_str = os.getenv("NEWS_FEEDS", "")
        news_feeds = (
            [feed.strip() for feed in news_feeds_str.split(",") if feed.strip()]
            if news_feeds_str
            else cls._get_default_news_feeds()
        )

        channel_id_str = os.getenv("NEWS_CHANNEL_ID", "0")
        try:
            channel_id = int(channel_id_str)
        except ValueError:
            channel_id = 0

        return cls(
            discord_token=os.getenv("DISCORD_TOKEN", ""),
            news_channel_id=channel_id,
            youtube_channels=youtube_channels,
            news_feeds=news_feeds,
            youtube_check_interval=int(os.getenv("YOUTUBE_CHECK_INTERVAL", "3600")),
            news_check_interval=int(os.getenv("NEWS_CHECK_INTERVAL", "1800")),
        )

    @staticmethod
    def _get_default_youtube_channels() -> list[str]:
        """Return default YouTube channel IDs for quantum computing content."""
        return [
            # Quantum computing focused channels
            "UCwlP-bPZmqpUuAi3L7q-FBw",  # Looking Glass Universe
            "UC7_gcs09iThXybpVgjHZ_7g",  # PBS Space Time
            "UCoxcjq-8xIDTYp3uz647V5A",  # Numberphile
            "UCYO_jab_esuFRV4b17AJtAw",  # 3Blue1Brown
            "UCkLHy_jxeaHTZCfGalg6QaA",  # Minute Physics
        ]

    @staticmethod
    def _get_default_news_feeds() -> list[str]:
        """Return default RSS feeds for quantum computing news."""
        return [
            # Quantum computing news sources
            "https://phys.org/rss-feed/search/?search=quantum+computing",
            "https://www.sciencedaily.com/rss/matter_energy/quantum_computing.xml",
            "https://quantumcomputingreport.com/feed/",
            "https://thequantuminsider.com/feed/",
        ]

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.discord_token:
            return False, "DISCORD_TOKEN is required"
        if not self.news_channel_id:
            return False, "NEWS_CHANNEL_ID is required"
        return True, None
