# Discord Scraping Instructions

## Quick Start

1. **Create Discord Bot**
   - Visit: https://discord.com/developers/applications
   - Click "New Application"
   - Name it (e.g., "AutoPPIA Monitor")
   - Go to "Bot" section
   - Click "Add Bot"
   - Copy the token

2. **Invite Bot to Server**
   - Go to "OAuth2" > "URL Generator"
   - Select scopes: `bot`
   - Select permissions: `Read Messages`, `Read Message History`, `View Channels`
   - Copy the generated URL and open it
   - Select AutoPPIA server: https://discord.gg/autoppia

3. **Set Token and Run**
   ```bash
   export DISCORD_BOT_TOKEN="your_token_here"
   python3 scripts/discord_scraper.py
   ```

## Manual Check

If you can't use a bot, manually check:
- **Discord**: https://discord.gg/autoppia
- **Important Channels**:
  - #announcements - Official updates
  - #miners - Miner discussions
  - #help - Support and help
  - #general - General discussions
  - #updates - Latest updates

## Output

Scraped data will be saved to:
- `docs/discord/discord_messages_TIMESTAMP.json`
- `docs/discord/discord_summary_TIMESTAMP.md`
- `docs/discord/discord_latest.json`
