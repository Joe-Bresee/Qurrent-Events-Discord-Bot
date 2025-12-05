"""Tests for the news feed cog."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.cogs.news_feed import NewsFeed


class TestNewsFeed:
    """Test cases for NewsFeed cog."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = MagicMock()
        bot.wait_until_ready = AsyncMock()
        bot.get_channel = MagicMock()
        return bot

    @pytest.fixture
    def news_feed(self, mock_bot):
        """Create a NewsFeed instance for testing."""
        return NewsFeed(
            bot=mock_bot,
            feed_urls=["https://example.com/feed"],
            news_channel_id=123456789,
            check_interval=1800,
        )

    def test_init(self, news_feed):
        """Test NewsFeed initialization."""
        assert len(news_feed.feed_urls) == 1
        assert news_feed.news_channel_id == 123456789
        assert news_feed.check_interval == 1800
        assert len(news_feed.seen_articles) == 0

    def test_get_article_id(self, news_feed):
        """Test article ID generation."""
        entry = {"link": "https://example.com/article1"}
        article_id = news_feed._get_article_id(entry)
        assert isinstance(article_id, str)
        assert len(article_id) == 16

        # Same entry should produce same ID
        article_id_2 = news_feed._get_article_id(entry)
        assert article_id == article_id_2

        # Different entry should produce different ID
        entry_2 = {"link": "https://example.com/article2"}
        article_id_3 = news_feed._get_article_id(entry_2)
        assert article_id != article_id_3

    def test_is_quantum_related_positive(self, news_feed):
        """Test quantum keyword detection for related articles."""
        # Articles that should be detected as quantum-related
        quantum_entries = [
            {"title": "New Quantum Computer Breakthrough", "summary": ""},
            {"title": "", "summary": "Scientists achieve qubit stability"},
            {"title": "IBM Quantum announces new processor", "summary": ""},
            {"title": "", "summary": "Entanglement experiment succeeds"},
            {"title": "Quantum supremacy achieved", "summary": ""},
            {"title": "IonQ releases new system", "summary": ""},
            {"title": "", "summary": "Quantum error correction improved"},
        ]

        for entry in quantum_entries:
            assert news_feed._is_quantum_related(entry), f"Should detect: {entry}"

    def test_is_quantum_related_negative(self, news_feed):
        """Test quantum keyword detection for unrelated articles."""
        # Articles that should NOT be detected as quantum-related
        non_quantum_entries = [
            {"title": "New iPhone Released", "summary": "Apple announces new phone"},
            {"title": "Stock Market Update", "summary": "Markets close higher today"},
            {"title": "Weather Forecast", "summary": "Rain expected tomorrow"},
        ]

        for entry in non_quantum_entries:
            assert not news_feed._is_quantum_related(entry), f"Should not detect: {entry}"

    def test_clean_html(self, news_feed):
        """Test HTML cleaning."""
        # Test basic HTML removal
        html_text = "<p>Hello <b>World</b></p>"
        assert news_feed._clean_html(html_text) == "Hello World"

        # Test entity replacement
        entity_text = "Tom &amp; Jerry &gt; Mickey"
        assert news_feed._clean_html(entity_text) == "Tom & Jerry > Mickey"

        # Test nbsp
        nbsp_text = "Hello&nbsp;World"
        assert news_feed._clean_html(nbsp_text) == "Hello World"


@pytest.mark.asyncio
class TestNewsFeedAsync:
    """Async test cases for NewsFeed cog."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = MagicMock()
        bot.wait_until_ready = AsyncMock()
        return bot

    @pytest.fixture
    def news_feed(self, mock_bot):
        """Create a NewsFeed instance for testing."""
        return NewsFeed(
            bot=mock_bot,
            feed_urls=["https://example.com/feed"],
            news_channel_id=123456789,
            check_interval=1800,
        )

    async def test_post_article(self, news_feed, mock_bot):
        """Test posting an article to Discord."""
        mock_channel = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        entry = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "summary": "This is a test article about quantum computing.",
            "published": "2024-01-01T00:00:00Z",
        }

        await news_feed._post_article(entry, "Test Source")

        # Verify channel.send was called
        mock_channel.send.assert_called_once()

        # Verify embed was created correctly
        call_args = mock_channel.send.call_args
        embed = call_args.kwargs.get("embed")
        assert embed is not None
        assert "Test Article" in embed.title

    async def test_post_article_no_channel(self, news_feed, mock_bot):
        """Test handling when Discord channel is not found."""
        mock_bot.get_channel.return_value = None

        entry = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "summary": "Test summary",
        }

        # Should not raise an exception
        await news_feed._post_article(entry, "Test Source")
