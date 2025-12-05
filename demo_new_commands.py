#!/usr/bin/env python3
"""
Test script to demonstrate the new dynamic source management commands.
"""

import asyncio
import discord
from datetime import datetime, timezone
from src.config import BotConfig

class CommandDemoBot:
    """Demo bot to show the new commands in action."""
    
    def __init__(self, token: str, channel_id: int):
        self.token = token
        self.channel_id = channel_id
        self.client = None
    
    async def connect(self):
        """Connect to Discord and demo commands."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            print(f"✅ Connected as {self.client.user}")
            await self.demo_help_command()
            await self.client.close()
        
        await self.client.start(self.token)
    
    async def demo_help_command(self):
        """Show the updated help command."""
        channel = self.client.get_channel(self.channel_id)
        if not channel:
            print(f"❌ Could not find channel {self.channel_id}")
            return
        
        print(f"📋 Sending updated !qhelp to #{channel.name}")
        
        # Updated help embed (matching the real bot)
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
                "from various sources\n"
                "• ➕ **Dynamic Sources** - Add new YouTube channels and RSS feeds on the fly!"
            ),
            inline=False,
        )

        embed.set_footer(text="UVic Quantum Computing Discord")

        await channel.send("**🆕 UPDATED BOT HELP - NEW COMMANDS AVAILABLE!**", embed=embed)
        print("✅ Updated help command sent!")

async def main():
    """Run the demo."""
    print("🚀 New Commands Demo")
    print("=" * 40)
    
    # Load config
    config = BotConfig.from_env()
    
    if not config.discord_token or not config.news_channel_id:
        print("❌ Please set DISCORD_TOKEN and NEWS_CHANNEL_ID in your .env file")
        return
    
    try:
        bot = CommandDemoBot(config.discord_token, config.news_channel_id)
        await bot.connect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())