"""Main bot module for Qurrent Events Discord Bot."""

import asyncio
import json
import logging
import os
import sys

import discord
from discord.ext import commands

from src.config import BotConfig
from src.cogs.youtube_feed import YouTubeFeed
from src.cogs.news_feed import NewsFeed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

DYNAMIC_SOURCES_FILE = "dynamic_sources.json"


def load_dynamic_sources():
    """Load dynamically added sources from file."""
    if os.path.exists(DYNAMIC_SOURCES_FILE):
        try:
            with open(DYNAMIC_SOURCES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load dynamic sources: {e}")
    
    return {"youtube_channels": [], "rss_feeds": []}


def save_dynamic_sources(youtube_channels, rss_feeds):
    """Save dynamically added sources to file."""
    try:
        data = {
            "youtube_channels": youtube_channels,
            "rss_feeds": rss_feeds
        }
        with open(DYNAMIC_SOURCES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save dynamic sources: {e}")


class QurrentEventsBot(commands.Bot):
    """Discord bot for quantum computing news and updates."""

    def __init__(self, config: BotConfig):
        """
        Initialize the bot.

        Args:
            config: Bot configuration
        """
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!q",
            intents=intents,
            description="Quantum computing news and updates for UVic Quantum Computing Discord",
        )

        self.config = config

    async def setup_hook(self) -> None:
        """Set up the bot before it connects."""
        # Load dynamic sources
        dynamic_sources = load_dynamic_sources()
        
        # Combine config sources with dynamic sources
        all_youtube_channels = list(set(self.config.youtube_channels + dynamic_sources["youtube_channels"]))
        all_rss_feeds = list(set(self.config.news_feeds + dynamic_sources["rss_feeds"]))
        
        # Add YouTube feed cog
        await self.add_cog(
            YouTubeFeed(
                self,
                channel_ids=all_youtube_channels,
                news_channel_id=self.config.news_channel_id,
                check_interval=self.config.youtube_check_interval,
            )
        )
        logger.info("YouTube feed cog loaded")

        # Add News feed cog
        await self.add_cog(
            NewsFeed(
                self,
                feed_urls=all_rss_feeds,
                news_channel_id=self.config.news_channel_id,
                check_interval=self.config.news_check_interval,
            )
        )
        logger.info("News feed cog loaded")

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")

        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for quantum news | !qhelp",
            )
        )

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands

        logger.error(f"Command error: {error}")


@commands.command(name="help")
async def qhelp(ctx: commands.Context) -> None:
    """Display help information."""
    embed = discord.Embed(
        title="🔮 Qurrent Events Bot",
        description="Your source for quantum computing news and updates!",
        color=discord.Color.purple(),
    )

    embed.add_field(
        name="📋 Basic Commands",
        value=(
            "`!qhelp` - Show this help message\n"
            "`!qyoutube` - Show YouTube monitoring status\n"
            "`!qnews` - Show news monitoring status\n"
            "`!qstatus` - Show overall bot status\n"
            "`!qlist-sources` - List all monitored sources"
        ),
        inline=False,
    )
    
    embed.add_field(
        name="➕ Add Sources",
        value=(
            "`!qadd-source-youtube UC1yNl2E66ZzKApQdRuTQ4tw`\n"
            "Add YouTube channel (use channel ID)\n\n"
            "`!qadd-source-rss https://example.com/feed.xml`\n"
            "Add RSS news feed"
        ),
        inline=False,
    )

    embed.add_field(
        name="Features",
        value=(
            "• 🎬 **YouTube Notifications** - Get alerts when quantum computing "
            "channels upload new videos\n"
            "• 📰 **News Updates** - Receive the latest quantum computing news "
            "from various sources"
        ),
        inline=False,
    )

    embed.set_footer(text="UVic Quantum Computing Discord")

    await ctx.send(embed=embed)


@commands.command(name="status")
async def status(ctx: commands.Context) -> None:
    """Display overall bot status."""
    bot = ctx.bot

    embed = discord.Embed(
        title="🔮 Qurrent Events Bot Status",
        color=discord.Color.green(),
    )

    embed.add_field(
        name="Bot",
        value=f"Online as {bot.user}",
        inline=True,
    )
    embed.add_field(
        name="Guilds",
        value=str(len(bot.guilds)),
        inline=True,
    )
    embed.add_field(
        name="Latency",
        value=f"{round(bot.latency * 1000)}ms",
        inline=True,
    )

    # Get cog statuses
    youtube_cog = bot.get_cog("YouTubeFeed")
    news_cog = bot.get_cog("NewsFeed")

    if youtube_cog:
        embed.add_field(
            name="YouTube",
            value=f"✅ Monitoring {len(youtube_cog.channel_ids)} channels",
            inline=True,
        )

    if news_cog:
        embed.add_field(
            name="News",
            value=f"✅ Monitoring {len(news_cog.feed_urls)} feeds",
            inline=True,
        )

    await ctx.send(embed=embed)


@commands.command(name="add-source-youtube")
async def add_youtube_source(ctx: commands.Context, channel_id: str) -> None:
    """
    Add a YouTube channel to monitor.
    
    Usage: !qadd-source-youtube UCxxxxxxxxxxxxx
    """
    bot = ctx.bot
    
    # Validate YouTube channel ID format
    if not channel_id.startswith('UC') or len(channel_id) != 24:
        await ctx.send("❌ Invalid YouTube channel ID format. Should be 24 characters starting with 'UC'")
        return
    
    # Get the YouTube feed cog
    youtube_cog = bot.get_cog("YouTubeFeed")
    if not youtube_cog:
        await ctx.send("❌ YouTube monitoring is not available")
        return
    
    # Check if already monitoring this channel
    if channel_id in youtube_cog.channel_ids:
        await ctx.send(f"⚠️ Already monitoring YouTube channel: `{channel_id}`")
        return
    
    # Add the channel
    youtube_cog.channel_ids.append(channel_id)
    
    # Save to persistent storage
    dynamic_sources = load_dynamic_sources()
    if channel_id not in dynamic_sources["youtube_channels"]:
        dynamic_sources["youtube_channels"].append(channel_id)
        save_dynamic_sources(dynamic_sources["youtube_channels"], dynamic_sources["rss_feeds"])
    
    embed = discord.Embed(
        title="✅ YouTube Channel Added",
        description=f"Now monitoring YouTube channel: `{channel_id}`",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Total Channels", 
        value=str(len(youtube_cog.channel_ids)), 
        inline=True
    )
    embed.set_footer(text="New videos from this channel will be posted here!")
    
    await ctx.send(embed=embed)
    logger.info(f"Added YouTube channel {channel_id} via Discord command")


@commands.command(name="add-source-rss")
async def add_rss_source(ctx: commands.Context, *, feed_url: str) -> None:
    """
    Add an RSS feed to monitor.
    
    Usage: !qadd-source-rss https://example.com/feed.xml
    """
    bot = ctx.bot
    
    # Basic URL validation
    if not feed_url.startswith(('http://', 'https://')):
        await ctx.send("❌ Invalid RSS feed URL. Must start with http:// or https://")
        return
    
    # Get the news feed cog
    news_cog = bot.get_cog("NewsFeed")
    if not news_cog:
        await ctx.send("❌ News monitoring is not available")
        return
    
    # Check if already monitoring this feed
    if feed_url in news_cog.feed_urls:
        await ctx.send(f"⚠️ Already monitoring RSS feed: `{feed_url}`")
        return
    
    # Add the feed
    news_cog.feed_urls.append(feed_url)
    
    # Save to persistent storage
    dynamic_sources = load_dynamic_sources()
    if feed_url not in dynamic_sources["rss_feeds"]:
        dynamic_sources["rss_feeds"].append(feed_url)
        save_dynamic_sources(dynamic_sources["youtube_channels"], dynamic_sources["rss_feeds"])
    
    embed = discord.Embed(
        title="✅ RSS Feed Added",
        description=f"Now monitoring RSS feed: `{feed_url}`",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Total Feeds", 
        value=str(len(news_cog.feed_urls)), 
        inline=True
    )
    embed.set_footer(text="Quantum-related articles from this feed will be posted here!")
    
    await ctx.send(embed=embed)
    logger.info(f"Added RSS feed {feed_url} via Discord command")


@commands.command(name="list-sources")
async def list_sources(ctx: commands.Context) -> None:
    """List all currently monitored sources."""
    bot = ctx.bot
    
    embed = discord.Embed(
        title="📋 Monitored Sources",
        color=discord.Color.purple()
    )
    
    # YouTube channels
    youtube_cog = bot.get_cog("YouTubeFeed")
    if youtube_cog:
        youtube_list = "\n".join([f"• `{ch}`" for ch in youtube_cog.channel_ids[:10]])
        if len(youtube_cog.channel_ids) > 10:
            youtube_list += f"\n... and {len(youtube_cog.channel_ids) - 10} more"
        
        embed.add_field(
            name=f"🎬 YouTube Channels ({len(youtube_cog.channel_ids)})",
            value=youtube_list or "None",
            inline=False
        )
    
    # RSS feeds
    news_cog = bot.get_cog("NewsFeed")
    if news_cog:
        rss_list = "\n".join([f"• {url[:50]}..." if len(url) > 50 else f"• {url}" for url in news_cog.feed_urls[:5]])
        if len(news_cog.feed_urls) > 5:
            rss_list += f"\n... and {len(news_cog.feed_urls) - 5} more"
        
        embed.add_field(
            name=f"📰 RSS Feeds ({len(news_cog.feed_urls)})",
            value=rss_list or "None",
            inline=False
        )
    
    await ctx.send(embed=embed)


def main() -> None:
    """Main entry point for the bot."""
    # Load configuration
    config = BotConfig.from_env()

    # Validate configuration
    is_valid, error = config.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error}")
        logger.error(
            "Please set the required environment variables:\n"
            "  DISCORD_TOKEN - Your Discord bot token\n"
            "  NEWS_CHANNEL_ID - The Discord channel ID for posting news"
        )
        sys.exit(1)

    # Create and run bot
    bot = QurrentEventsBot(config)

    # Add commands
    bot.add_command(qhelp)
    bot.add_command(status)
    bot.add_command(add_youtube_source)
    bot.add_command(add_rss_source)
    bot.add_command(list_sources)

    logger.info("Starting Qurrent Events Bot...")
    bot.run(config.discord_token)


if __name__ == "__main__":
    main()
