#!/usr/bin/env python3
"""
Test script to demonstrate what bot posts look like.

This script will create mock examples of YouTube and RSS feed posts
that your bot would send to Discord.
"""

import asyncio
import discord
from datetime import datetime, timezone
from src.config import BotConfig

class MockBot:
    """Mock bot for testing post formats."""
    
    def __init__(self, token: str, channel_id: int):
        self.token = token
        self.channel_id = channel_id
        self.client = None
    
    async def connect(self):
        """Connect to Discord."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            print(f"✅ Connected as {self.client.user}")
            await self.send_examples()
            await self.client.close()
        
        await self.client.start(self.token)
    
    async def send_examples(self):
        """Send example posts."""
        channel = self.client.get_channel(self.channel_id)
        if not channel:
            print(f"❌ Could not find channel {self.channel_id}")
            return
        
        print(f"📺 Sending example posts to #{channel.name}")
        
        # Example YouTube Video Post
        youtube_embed = discord.Embed(
            title="🎬 New Video: The Quantum Eraser Experiment",
            url="https://www.youtube.com/watch?v=8ORLN_KwAgs",
            description="**Sabine Hossenfelder** just uploaded a new video!",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc),
        )
        
        youtube_embed.set_thumbnail(url="https://i.ytimg.com/vi/8ORLN_KwAgs/mqdefault.jpg")
        youtube_embed.add_field(name="Published", value="2 hours ago", inline=True)
        youtube_embed.set_footer(text="Qurrent Events • YouTube")
        
        await channel.send("**🎬 NEW YOUTUBE VIDEO EXAMPLE:**", embed=youtube_embed)
        
        # Small delay between posts
        await asyncio.sleep(2)
        
        # Example News Article Post
        news_embed = discord.Embed(
            title="🔬 IBM Unveils 1000-Qubit Quantum Processor",
            url="https://thequantuminsider.com/2024/12/04/ibm-1000-qubit-processor/",
            description="IBM has announced a breakthrough 1000-qubit quantum processor, marking a significant milestone in quantum computing development...",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )
        
        news_embed.add_field(name="Source", value="The Quantum Insider", inline=True)
        news_embed.add_field(name="Published", value="3 hours ago", inline=True)
        news_embed.add_field(name="🔑 Keywords", value="quantum processor, IBM, qubits", inline=False)
        news_embed.set_footer(text="Qurrent Events • News Feed")
        
        await channel.send("**📰 NEW NEWS ARTICLE EXAMPLE:**", embed=news_embed)
        
        print("✅ Example posts sent!")

async def main():
    """Run the test."""
    print("🧪 Discord Bot Post Examples")
    print("=" * 40)
    
    # Load config
    config = BotConfig.from_env()
    
    if not config.discord_token or not config.news_channel_id:
        print("❌ Please set DISCORD_TOKEN and NEWS_CHANNEL_ID in your .env file")
        return
    
    try:
        bot = MockBot(config.discord_token, config.news_channel_id)
        await bot.connect()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your bot is added to the Discord server!")

if __name__ == "__main__":
    asyncio.run(main())