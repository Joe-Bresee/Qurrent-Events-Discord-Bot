"""Tests for the YouTube feed cog."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.cogs.youtube_feed import YouTubeFeed


class TestYouTubeFeed:
    """Test cases for YouTubeFeed cog."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = MagicMock()
        bot.wait_until_ready = AsyncMock()
        bot.get_channel = MagicMock()
        return bot

    @pytest.fixture
    def youtube_feed(self, mock_bot):
        """Create a YouTubeFeed instance for testing."""
        return YouTubeFeed(
            bot=mock_bot,
            channel_ids=["UC123", "UC456"],
            news_channel_id=123456789,
            check_interval=3600,
        )

    def test_init(self, youtube_feed):
        """Test YouTubeFeed initialization."""
        assert len(youtube_feed.channel_ids) == 2
        assert youtube_feed.news_channel_id == 123456789
        assert youtube_feed.check_interval == 3600
        assert len(youtube_feed.last_video_ids) == 0

    def test_channel_ids_stored(self, youtube_feed):
        """Test that channel IDs are stored correctly."""
        assert "UC123" in youtube_feed.channel_ids
        assert "UC456" in youtube_feed.channel_ids


@pytest.mark.asyncio
class TestYouTubeFeedAsync:
    """Async test cases for YouTubeFeed cog."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = MagicMock()
        bot.wait_until_ready = AsyncMock()
        return bot

    @pytest.fixture
    def youtube_feed(self, mock_bot):
        """Create a YouTubeFeed instance for testing."""
        return YouTubeFeed(
            bot=mock_bot,
            channel_ids=["UC123", "UC456"],
            news_channel_id=123456789,
            check_interval=3600,
        )

    async def test_post_video(self, youtube_feed, mock_bot):
        """Test posting a video to Discord."""
        mock_channel = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        entry = {
            "title": "Test Video",
            "link": "https://youtube.com/watch?v=test123",
            "published": "2024-01-01T00:00:00Z",
        }

        await youtube_feed._post_video(entry, "Test Channel")

        # Verify channel.send was called
        mock_channel.send.assert_called_once()

        # Verify embed was created correctly
        call_args = mock_channel.send.call_args
        embed = call_args.kwargs.get("embed")
        assert embed is not None
        assert "Test Video" in embed.title

    async def test_post_video_no_channel(self, youtube_feed, mock_bot):
        """Test handling when Discord channel is not found."""
        mock_bot.get_channel.return_value = None

        entry = {
            "title": "Test Video",
            "link": "https://youtube.com/watch?v=test123",
        }

        # Should not raise an exception
        await youtube_feed._post_video(entry, "Test Channel")

    async def test_post_video_with_thumbnail(self, youtube_feed, mock_bot):
        """Test posting a video with thumbnail."""
        mock_channel = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        entry = {
            "title": "Test Video",
            "link": "https://youtube.com/watch?v=test123",
            "published": "2024-01-01T00:00:00Z",
            "media_thumbnail": [{"url": "https://i.ytimg.com/vi/test123/maxresdefault.jpg"}],
        }

        await youtube_feed._post_video(entry, "Test Channel")

        # Verify channel.send was called
        mock_channel.send.assert_called_once()
