# Qurrent Events Discord Bot

Discord bot for sending news and sources of Quantum computing and adjacent news to the UVic Quantum Computing Discord.

## Features

- 🎬 **YouTube Notifications** - Automatically posts when quantum computing YouTube channels upload new videos
- 📰 **News Feed Updates** - Aggregates and posts quantum computing news from various RSS feeds
- 🔍 **Smart Filtering** - Filters news articles to only post quantum-related content

## Default Sources

### YouTube Channels
- Looking Glass Universe
- PBS Space Time
- Numberphile
- 3Blue1Brown
- Minute Physics

### News Feeds
- Phys.org Quantum Computing
- Science Daily Quantum Computing
- Quantum Computing Report
- The Quantum Insider

## Setup

### Prerequisites
- Python 3.10 or higher
- A Discord bot token (create one at [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Joe-Bresee/Qurrent-Events-Discord-Bot.git
   cd Qurrent-Events-Discord-Bot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your configuration:
   - `DISCORD_TOKEN` - Your Discord bot token (required)
   - `NEWS_CHANNEL_ID` - The channel ID where news will be posted (required)

### Running the Bot

```bash
python -m src.bot
```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `NEWS_CHANNEL_ID` | Discord channel ID for posting news | Required |
| `YOUTUBE_CHANNELS` | Comma-separated YouTube channel IDs | Default list |
| `NEWS_FEEDS` | Comma-separated RSS feed URLs | Default list |
| `YOUTUBE_CHECK_INTERVAL` | Seconds between YouTube checks | 3600 (1 hour) |
| `NEWS_CHECK_INTERVAL` | Seconds between news checks | 1800 (30 min) |

## Commands

| Command | Description |
|---------|-------------|
| `!qhelp` | Show help information |
| `!qstatus` | Show bot status |
| `!qyoutube` | Show YouTube monitoring status |
| `!qnews` | Show news monitoring status |

## Development

### Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Project Structure

```
Qurrent-Events-Discord-Bot/
├── src/
│   ├── __init__.py
│   ├── bot.py           # Main bot application
│   ├── config.py        # Configuration management
│   └── cogs/
│       ├── __init__.py
│       ├── youtube_feed.py  # YouTube monitoring
│       └── news_feed.py     # News feed monitoring
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_youtube_feed.py
│   └── test_news_feed.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## License

This project is for the UVic Quantum Computing Discord community.
