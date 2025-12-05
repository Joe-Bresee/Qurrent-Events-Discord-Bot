#!/usr/bin/env python3
"""
Qurrent Events Discord Bot - Main entry point

This script initializes and runs the Discord bot with the configured settings.
Make sure to set up your .env file with the required Discord tokens before running.
"""

import asyncio
import logging
import sys

from src.bot import QurrentEventsBot
from src.config import BotConfig

logger = logging.getLogger(__name__)


async def main():
    """Main function to initialize and run the bot."""
    # Load configuration
    config = BotConfig.from_env()
    
    # Validate configuration
    is_valid, error = config.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error}")
        logger.error("Please check your .env file and ensure all required values are set.")
        sys.exit(1)
    
    # Initialize and run bot
    bot = QurrentEventsBot(config)
    
    try:
        logger.info("Starting Qurrent Events Discord Bot...")
        logger.info(f"Monitoring {len(config.youtube_channels)} YouTube channels")
        logger.info(f"Monitoring {len(config.news_feeds)} news feeds")
        
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())