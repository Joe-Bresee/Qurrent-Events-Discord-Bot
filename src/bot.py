"""Main bot module for Qurrent Events Discord Bot."""

import asyncio
import logging
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
        # Add YouTube feed cog
        await self.add_cog(
            YouTubeFeed(
                self,
                channel_ids=self.config.youtube_channels,
                news_channel_id=self.config.news_channel_id,
                check_interval=self.config.youtube_check_interval,
            )
        )
        logger.info("YouTube feed cog loaded")

        # Add News feed cog
        await self.add_cog(
            NewsFeed(
                self,
                feed_urls=self.config.news_feeds,
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
        name="Commands",
        value=(
            "`!qhelp` - Show this help message\n"
            "`!qyoutube` - Show YouTube monitoring status\n"
            "`!qnews` - Show news monitoring status\n"
            "`!qstatus` - Show overall bot status"
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

    logger.info("Starting Qurrent Events Bot...")
    bot.run(config.discord_token)


if __name__ == "__main__":
    main()
