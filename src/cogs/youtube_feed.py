"""YouTube feed monitoring cog for the Discord bot."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import discord
import feedparser
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)


class YouTubeFeed(commands.Cog):
    """Cog for monitoring YouTube channels and posting new videos."""

    def __init__(
        self,
        bot: commands.Bot,
        channel_ids: list[str],
        news_channel_id: int,
        check_interval: int = 3600,
    ):
        """
        Initialize the YouTube feed cog.

        Args:
            bot: The Discord bot instance
            channel_ids: List of YouTube channel IDs to monitor
            news_channel_id: Discord channel ID to post updates to
            check_interval: Interval between checks in seconds
        """
        self.bot = bot
        self.channel_ids = channel_ids
        self.news_channel_id = news_channel_id
        self.check_interval = check_interval
        self.last_video_ids: dict[str, str] = {}
        self._check_task: Optional[tasks.Loop] = None

    async def cog_load(self) -> None:
        """Called when the cog is loaded."""
        # Create the check task dynamically with the configured interval
        @tasks.loop(seconds=self.check_interval)
        async def check_youtube():
            await self._check_youtube_feeds()

        @check_youtube.before_loop
        async def before_check():
            await self.bot.wait_until_ready()

        self._check_task = check_youtube
        self._check_task.start()
        logger.info("YouTube feed monitoring started")

    async def cog_unload(self) -> None:
        """Called when the cog is unloaded."""
        if self._check_task:
            self._check_task.cancel()
        logger.info("YouTube feed monitoring stopped")

    async def _check_youtube_feeds(self) -> None:
        """Check all configured YouTube channels for new videos."""
        for channel_id in self.channel_ids:
            try:
                await self._check_channel(channel_id)
            except Exception as e:
                logger.error(f"Error checking YouTube channel {channel_id}: {e}")
            # Small delay between channel checks to avoid rate limiting
            await asyncio.sleep(2)

    async def _check_channel(self, channel_id: str) -> None:
        """
        Check a single YouTube channel for new videos.

        Args:
            channel_id: The YouTube channel ID to check
        """
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

        # Run feedparser in executor to avoid blocking
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

        if feed.bozo:
            logger.warning(f"Error parsing feed for channel {channel_id}: {feed.bozo_exception}")
            return

        if not feed.entries:
            return

        latest_entry = feed.entries[0]
        video_id = latest_entry.get("yt_videoid", "")

        if not video_id:
            return

        # Check if this is a new video
        if channel_id in self.last_video_ids:
            if self.last_video_ids[channel_id] == video_id:
                return  # Already posted this video
        else:
            # First run for this channel, just store the ID without posting
            self.last_video_ids[channel_id] = video_id
            logger.info(f"Initialized tracking for channel {channel_id}, latest video: {video_id}")
            return

        # New video detected!
        self.last_video_ids[channel_id] = video_id
        await self._post_video(latest_entry, feed.feed.get("title", "Unknown Channel"))

    async def _post_video(self, entry: dict, channel_name: str) -> None:
        """
        Post a new video notification to Discord.

        Args:
            entry: The feed entry containing video information
            channel_name: The name of the YouTube channel
        """
        channel = self.bot.get_channel(self.news_channel_id)
        if not channel:
            logger.error(f"Could not find Discord channel {self.news_channel_id}")
            return

        video_title = entry.get("title", "Unknown Title")
        video_url = entry.get("link", "")
        published = entry.get("published", "")

        embed = discord.Embed(
            title=f"🎬 New Video: {video_title}",
            url=video_url,
            description=f"**{channel_name}** just uploaded a new video!",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc),
        )

        # Try to get thumbnail
        if "media_thumbnail" in entry and entry["media_thumbnail"]:
            embed.set_thumbnail(url=entry["media_thumbnail"][0].get("url", ""))

        embed.add_field(name="Published", value=published or "Unknown", inline=True)
        embed.set_footer(text="Qurrent Events • YouTube")

        await channel.send(embed=embed)
        logger.info(f"Posted new video: {video_title} from {channel_name}")

    @commands.command(name="youtube")
    async def youtube_status(self, ctx: commands.Context) -> None:
        """Display the current YouTube monitoring status."""
        embed = discord.Embed(
            title="📺 YouTube Monitoring Status",
            color=discord.Color.red(),
        )

        embed.add_field(
            name="Channels Monitored",
            value=str(len(self.channel_ids)),
            inline=True,
        )
        embed.add_field(
            name="Check Interval",
            value=f"{self.check_interval // 60} minutes",
            inline=True,
        )
        embed.add_field(
            name="Videos Tracked",
            value=str(len(self.last_video_ids)),
            inline=True,
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Set up the YouTube feed cog."""
    # This is called when using bot.load_extension()
    # Configuration should be passed via bot.youtube_config
    config = getattr(bot, "youtube_config", {})
    await bot.add_cog(
        YouTubeFeed(
            bot,
            channel_ids=config.get("channel_ids", []),
            news_channel_id=config.get("news_channel_id", 0),
            check_interval=config.get("check_interval", 3600),
        )
    )
