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
from src.cogs.management import ManagementCommands

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
        # Remove default help command first
        self.remove_command('help')
        
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

        # Add management commands cog
        await self.add_cog(ManagementCommands(self))
        logger.info("Management commands cog loaded")

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


# Management commands are now in src/cogs/management.py


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

    logger.info("Starting Qurrent Events Bot...")
    bot.run(config.discord_token)


if __name__ == "__main__":
    main()
