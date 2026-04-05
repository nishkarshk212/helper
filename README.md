# Telegram Group Management Bot

A Python-based Telegram bot for managing groups with an interactive settings panel.

## Features

- ✅ **Welcome Messages** - Automatically welcome new members with customizable messages
- 🛡️ **Anti-Spam Protection** - Detect and remove spam messages
- 🌊 **Anti-Flood Protection** - Prevent message flooding with configurable limits
- 🔗 **Link Control** - Allow or block links in your group
- ⚙️ **Interactive Settings Panel** - Easy-to-use inline keyboard for configuration
- 💾 **Persistent Settings** - All settings saved in SQLite database

## Setup Instructions

### 1. Create Your Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Bot Token

Create a `config.txt` file and add your bot token:

```bash
cp config.txt.example config.txt
# Edit config.txt and add your token
```

Or set it as an environment variable:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### 4. Run the Bot

```bash
python bot.py
```

## Usage

### Commands

- `/start` - Start the bot (for private chat)
- `/help` - Show help message
- `/settings` - Open the settings panel (admins only, in groups)

### Settings Panel Features

The settings panel provides buttons to toggle:

1. **Welcome Messages** - Enable/disable automatic welcome messages
2. **Anti-Spam** - Enable/disable spam detection and removal
3. **Anti-Flood** - Enable/disable flood protection
4. **Allow Links** - Toggle whether links are allowed
5. **CAPTCHA** - Enable/disable CAPTCHA verification (coming soon)
6. **Edit Welcome Message** - Customize the welcome message (use `{user}` to mention new members)
7. **Flood Settings** - Configure flood limit (3, 5, or 10 messages per 10 seconds)

### Adding Bot to Your Group

1. Add the bot to your group
2. Make the bot an admin (required for deleting messages and managing the group)
3. Use `/settings` to configure the bot

## File Structure

```
group-help/
├── bot.py              # Main bot application
├── database.py         # Database models and functions
├── settings.py         # Settings panel handlers
├── handlers.py         # Group management feature handlers
├── requirements.txt    # Python dependencies
├── config.txt.example  # Configuration template
└── group_bot.db        # SQLite database (auto-created)
```

## Requirements

- Python 3.8+
- python-telegram-bot 20.7
- SQLAlchemy 2.0.23

## Notes

- The bot needs admin privileges in the group to delete messages and manage settings
- All group settings are stored in a local SQLite database (`group_bot.db`)
- The bot uses polling mode, which is suitable for small to medium-sized groups

## License

This project is open source and available for personal and commercial use.
# helper
