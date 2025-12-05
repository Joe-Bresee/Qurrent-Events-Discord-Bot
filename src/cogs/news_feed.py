"""News feed monitoring cog for the Discord bot."""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import discord
import feedparser
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)


class NewsFeed(commands.Cog):
    """Cog for monitoring news RSS feeds and posting new articles."""

    def __init__(
        self,
        bot: commands.Bot,
        feed_urls: list[str],
        news_channel_id: int,
        check_interval: int = 1800,
    ):
        """
        Initialize the news feed cog.

        Args:
            bot: The Discord bot instance
            feed_urls: List of RSS feed URLs to monitor
            news_channel_id: Discord channel ID to post updates to
            check_interval: Interval between checks in seconds
        """
        self.bot = bot
        self.feed_urls = feed_urls
        self.news_channel_id = news_channel_id
        self.check_interval = check_interval
        self.seen_articles: set[str] = set()
        self._check_task: Optional[tasks.Loop] = None
        self._initialized = False

    async def cog_load(self) -> None:
        """Called when the cog is loaded."""
        # Create the check task dynamically with the configured interval
        @tasks.loop(seconds=self.check_interval)
        async def check_news():
            await self._check_news_feeds()

        @check_news.before_loop
        async def before_check():
            await self.bot.wait_until_ready()

        self._check_task = check_news
        self._check_task.start()
        logger.info("News feed monitoring started")

    async def cog_unload(self) -> None:
        """Called when the cog is unloaded."""
        if self._check_task:
            self._check_task.cancel()
        logger.info("News feed monitoring stopped")

    def _get_article_id(self, entry: dict) -> str:
        """
        Generate a unique ID for an article.

        Args:
            entry: The feed entry

        Returns:
            A unique hash string for the article
        """
        # Use link or title+summary as unique identifier
        unique_str = entry.get("link", "") or (
            entry.get("title", "") + entry.get("summary", "")
        )
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

    async def _check_news_feeds(self) -> None:
        """Check all configured news feeds for new articles."""
        for feed_url in self.feed_urls:
            try:
                await self._check_feed(feed_url)
            except Exception as e:
                logger.error(f"Error checking news feed {feed_url}: {e}")
            # Small delay between feed checks
            await asyncio.sleep(2)

        # Mark as initialized after first run
        if not self._initialized:
            self._initialized = True
            logger.info(f"News feed monitoring initialized with {len(self.seen_articles)} articles tracked")

    async def _check_feed(self, feed_url: str) -> None:
        """
        Check a single news feed for new articles.

        Args:
            feed_url: The RSS feed URL to check
        """
        # Run feedparser in executor to avoid blocking
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

        if feed.bozo:
            logger.warning(f"Error parsing feed {feed_url}: {feed.bozo_exception}")
            return

        feed_title = feed.feed.get("title", "Unknown Source")

        for entry in feed.entries[:10]:  # Check latest 10 entries
            article_id = self._get_article_id(entry)

            if article_id in self.seen_articles:
                continue

            self.seen_articles.add(article_id)

            # Skip posting during initialization
            if not self._initialized:
                continue

            # Check if article is quantum computing related
            if self._is_quantum_related(entry):
                await self._post_article(entry, feed_title)

    def _is_quantum_related(self, entry: dict) -> bool:
        """
        Check if an article is related to quantum computing.

        Args:
            entry: The feed entry to check

        Returns:
            True if the article appears to be quantum-related
        """
        quantum_keywords = [
            "quantum",
            "qubit",
            "qubits",
            "superposition",
            "entanglement",
            "quantum computer",
            "quantum computing",
            "quantum supremacy",
            "quantum advantage",
            "quantum processor",
            "quantum algorithm",
            "quantum cryptography",
            "quantum network",
            "quantum internet",
            "quantum simulation",
            "quantum error",
            "quantum gate",
            "ibm quantum",
            "google quantum",
            "d-wave",
            "ionq",
            "rigetti",
            "quantum machine learning",
        ]

        # Check title and summary
        title = entry.get("title", "").lower()
        summary = entry.get("summary", "").lower()
        content = title + " " + summary

        return any(keyword in content for keyword in quantum_keywords)

    async def _post_article(self, entry: dict, source_name: str) -> None:
        """
        Post a new article notification to Discord.

        Args:
            entry: The feed entry containing article information
            source_name: The name of the news source
        """
        channel = self.bot.get_channel(self.news_channel_id)
        if not channel:
            logger.error(f"Could not find Discord channel {self.news_channel_id}")
            return

        title = entry.get("title", "Unknown Title")
        url = entry.get("link", "")
        summary = entry.get("summary", "No summary available.")

        # Truncate summary if too long
        if len(summary) > 300:
            summary = summary[:297] + "..."

        # Clean up HTML from summary
        summary = self._clean_html(summary)

        embed = discord.Embed(
            title=f"📰 {title}",
            url=url,
            description=summary,
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(name="Source", value=source_name, inline=True)

        # Try to get publication date
        published = entry.get("published", "")
        if published:
            embed.add_field(name="Published", value=published[:25], inline=True)

        embed.set_footer(text="Qurrent Events • News")

        await channel.send(embed=embed)
        logger.info(f"Posted news article: {title} from {source_name}")

    def _clean_html(self, text: str) -> str:
        """
        Remove basic HTML tags from text.

        Args:
            text: The text to clean

        Returns:
            Text with HTML tags removed
        """
        import re

        clean = re.sub(r"<[^>]+>", "", text)
        clean = clean.replace("&nbsp;", " ")
        clean = clean.replace("&amp;", "&")
        clean = clean.replace("&lt;", "<")
        clean = clean.replace("&gt;", ">")
        clean = clean.replace("&quot;", '"')
        return clean.strip()

    @commands.command(name="news")
    async def news_status(self, ctx: commands.Context) -> None:
        """Display the current news monitoring status."""
        embed = discord.Embed(
            title="📰 News Monitoring Status",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="Feeds Monitored",
            value=str(len(self.feed_urls)),
            inline=True,
        )
        embed.add_field(
            name="Check Interval",
            value=f"{self.check_interval // 60} minutes",
            inline=True,
        )
        embed.add_field(
            name="Articles Tracked",
            value=str(len(self.seen_articles)),
            inline=True,
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Set up the news feed cog."""
    # This is called when using bot.load_extension()
    # Configuration should be passed via bot.news_config
    config = getattr(bot, "news_config", {})
    await bot.add_cog(
        NewsFeed(
            bot,
            feed_urls=config.get("feed_urls", []),
            news_channel_id=config.get("news_channel_id", 0),
            check_interval=config.get("check_interval", 1800),
        )
    )
