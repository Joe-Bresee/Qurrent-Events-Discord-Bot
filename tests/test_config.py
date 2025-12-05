"""Tests for the configuration module."""

import os
import pytest
from unittest.mock import patch

from src.config import BotConfig


class TestBotConfig:
    """Test cases for BotConfig class."""

    def test_default_youtube_channels(self):
        """Test that default YouTube channels are returned."""
        channels = BotConfig._get_default_youtube_channels()
        assert isinstance(channels, list)
        assert len(channels) > 0
        # All channel IDs should be non-empty strings
        for channel in channels:
            assert isinstance(channel, str)
            assert len(channel) > 0

    def test_default_news_feeds(self):
        """Test that default news feeds are returned."""
        feeds = BotConfig._get_default_news_feeds()
        assert isinstance(feeds, list)
        assert len(feeds) > 0
        # All feeds should be valid URLs
        for feed in feeds:
            assert isinstance(feed, str)
            assert feed.startswith("http")

    def test_validate_missing_token(self):
        """Test validation fails without Discord token."""
        config = BotConfig(
            discord_token="",
            news_channel_id=123456789,
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "DISCORD_TOKEN" in error

    def test_validate_missing_channel(self):
        """Test validation fails without channel ID."""
        config = BotConfig(
            discord_token="test_token",
            news_channel_id=0,
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "NEWS_CHANNEL_ID" in error

    def test_validate_success(self):
        """Test validation succeeds with valid config."""
        config = BotConfig(
            discord_token="test_token",
            news_channel_id=123456789,
        )
        is_valid, error = config.validate()
        assert is_valid is True
        assert error is None

    @patch.dict(
        os.environ,
        {
            "DISCORD_TOKEN": "test_token",
            "NEWS_CHANNEL_ID": "123456789",
            "YOUTUBE_CHECK_INTERVAL": "7200",
            "NEWS_CHECK_INTERVAL": "3600",
        },
    )
    def test_from_env(self):
        """Test loading configuration from environment variables."""
        config = BotConfig.from_env()
        assert config.discord_token == "test_token"
        assert config.news_channel_id == 123456789
        assert config.youtube_check_interval == 7200
        assert config.news_check_interval == 3600

    @patch.dict(
        os.environ,
        {
            "DISCORD_TOKEN": "test_token",
            "NEWS_CHANNEL_ID": "123456789",
            "YOUTUBE_CHANNELS": "channel1, channel2, channel3",
        },
    )
    def test_from_env_custom_youtube_channels(self):
        """Test loading custom YouTube channels from environment."""
        config = BotConfig.from_env()
        assert config.youtube_channels == ["channel1", "channel2", "channel3"]

    @patch.dict(
        os.environ,
        {
            "DISCORD_TOKEN": "test_token",
            "NEWS_CHANNEL_ID": "123456789",
            "NEWS_FEEDS": "https://example1.com/feed,https://example2.com/feed",
        },
    )
    def test_from_env_custom_news_feeds(self):
        """Test loading custom news feeds from environment."""
        config = BotConfig.from_env()
        assert config.news_feeds == [
            "https://example1.com/feed",
            "https://example2.com/feed",
        ]

    @patch.dict(
        os.environ,
        {
            "DISCORD_TOKEN": "test_token",
            "NEWS_CHANNEL_ID": "invalid",
        },
    )
    def test_from_env_invalid_channel_id(self):
        """Test handling of invalid channel ID."""
        config = BotConfig.from_env()
        assert config.news_channel_id == 0
