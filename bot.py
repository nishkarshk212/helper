"""
Main bot application
"""
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# Load environment variables from .env file
load_dotenv()

# Get log group ID
LOG_GROUP_ID = os.getenv('LOG_GROUP_ID')

from settings import (
    show_settings_panel,
    handle_settings_callback,
    handle_welcome_message_input,
    handle_goodbye_message_input,
    handle_media_message,
    handle_caption_input,
    handle_button_callback,
    handle_button_input,
    handle_self_destruct_time_input
)
from font import to_monospace_uppercase
from handlers import (
    handle_new_member,
    handle_left_member,
    handle_self_destruct_message,
    clean_service_messages
)
from user_management import (
    handle_ban_user,
    handle_warn_user,
    handle_mute_user,
    handle_unmute_user,
    handle_promote_user,
    handle_demote_user,
    handle_id_command,
    handle_info_command,
    handle_admins_command,
    handle_permission_toggle,
    handle_confirm_promote
)
from blocked_words import (
    handle_blockword_command,
    handle_unblockword_command,
    handle_blockedwords_command,
    check_blocked_words
)
from filters import (
    handle_filter_command,
    handle_filters_list,
    handle_stop_filter,
    handle_stopall_filters,
    check_filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context):
    """Send a message when the command /start is issued."""
    # Create inline keyboard with "Add to Group" button
    keyboard = [
        [InlineKeyboardButton(
            "➕ Add to Group", 
            url=f"https://t.me/{context.bot.username}?startgroup=true"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = to_monospace_uppercase(
        "👋 Hi! I'm a Group Management Bot.\n\n"
        "Add me to your group and use /settings to configure group settings.\n\n"
        "Available commands:\n"
        "/settings - Open group settings panel\n"
        "/help - Show help message"
    )
    
    await update.message.reply_text(
        message_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context):
    """Send a message when the command /help is issued."""
    message_text = to_monospace_uppercase(
        "Group Management Bot Help\n\n"
        "Commands:\n"
        "/settings - Open the settings panel (admins only)\n"
        "/help - Show this help message\n\n"
        "User Management (Creator):\n"
        "/ban - Ban a user (reply to message)\n"
        "/warn - Warn a user (3 warnings = auto-ban)\n"
        "/mute - Mute a user (no messages)\n"
        "/unmute - Unmute a user\n"
        "/promote - Promote user with custom permissions (toggle buttons)\n"
        "/demote - Remove admin privileges from a user\n\n"
        "User Info:\n"
        "/id - Get user ID (reply to message or use user ID)\n"
        "/info - Get detailed user information (reply to message)\n"
        "/admins - List all custom admins with permissions\n\n"
        "Content Moderation:\n"
        "/blockword <word> - Block a word/phrase (deletes messages containing it)\n"
        "/unblockword <word> - Remove a blocked word\n"
        "/blockedwords - List all blocked words\n\n"
        "Filters (Auto-reply):\n"
        "/filter <trigger> - Add filter (reply to message with content)\n"
        "/filters - List all chat filters\n"
        "/stop <trigger> - Remove a filter\n"
        "/stopall - Remove ALL filters (creator only)\n\n"
        "Filter Examples:\n"
        "1. Send photo/video/sticker/text\n"
        "2. Reply to it with: /filter trigger\n"
        "3. When someone types 'trigger', bot replies with your content!\n\n"
        "Features:\n"
        "• Custom welcome messages (text, photo, video, document)\n"
        "• Custom goodbye messages (text, photo, video, document)\n"
        "• Inline buttons for welcome/goodbye messages\n"
        "• Self-destruct messages (auto-delete with custom timer)\n"
        "• Clean service messages (join, leave, invite, voice chat)\n"
        "• User management (ban, warn, mute, promote, demote)\n"
        "• Custom admin roles with permission control via toggle buttons\n"
        "• Smart filters (auto-reply to keywords with any content)\n\n"
        "To configure settings, use /settings in your group."
    )
    
    await update.message.reply_text(
        message_text,
        parse_mode='HTML'
    )


async def error_handler(update: object, context) -> None:
    """Log errors caused by updates."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Send error to log group if configured
    if LOG_GROUP_ID:
        try:
            error_message = (
                f"❌ <b>Error Occurred</b>\n\n"
                f"<b>Error:</b> {context.error}\n"
                f"<b>Update:</b> {update}\n"
            )
            await context.bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=error_message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to send error to log group: {e}")


def main():
    """Start the bot."""
    # Get the bot token from environment variable or config file
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        # Try to read from config.txt
        try:
            with open('config.txt', 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            print("Error: Please set TELEGRAM_BOT_TOKEN environment variable or create config.txt with your bot token")
            print("Get your token from @BotFather on Telegram")
            return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", show_settings_panel))
    application.add_handler(CommandHandler("ban", handle_ban_user))
    application.add_handler(CommandHandler("warn", handle_warn_user))
    application.add_handler(CommandHandler("mute", handle_mute_user))
    application.add_handler(CommandHandler("unmute", handle_unmute_user))
    application.add_handler(CommandHandler("promote", handle_promote_user))
    application.add_handler(CommandHandler("demote", handle_demote_user))
    application.add_handler(CommandHandler("id", handle_id_command))
    application.add_handler(CommandHandler("info", handle_info_command))
    application.add_handler(CommandHandler("admins", handle_admins_command))
    application.add_handler(CommandHandler("blockword", handle_blockword_command))
    application.add_handler(CommandHandler("unblockword", handle_unblockword_command))
    application.add_handler(CommandHandler("blockedwords", handle_blockedwords_command))
    application.add_handler(CommandHandler("filter", handle_filter_command))
    application.add_handler(CommandHandler("filters", handle_filters_list))
    application.add_handler(CommandHandler("stop", handle_stop_filter))
    application.add_handler(CommandHandler("stopall", handle_stopall_filters))
    
    # Register callback query handlers (order matters - specific patterns first)
    application.add_handler(CallbackQueryHandler(handle_permission_toggle, pattern="^pt_"))
    application.add_handler(CallbackQueryHandler(handle_confirm_promote, pattern="^cp_"))
    application.add_handler(CallbackQueryHandler(handle_button_callback, pattern="^(add_welcome_buttons|skip_welcome_buttons|add_goodbye_buttons|skip_goodbye_buttons|remove_welcome_buttons|remove_goodbye_buttons)$"))
    application.add_handler(CallbackQueryHandler(handle_settings_callback))
    
    # Register message handlers
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        handle_new_member
    ))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        handle_left_member
    ))
    
    # Blocked words checker (MUST be before other text handlers)
    application.add_handler(MessageHandler(
        filters.TEXT | filters.CAPTION,
        check_blocked_words
    ))
    
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.ALL,
        handle_media_message
    ))
    
    # Register state-based handlers FIRST (before general text handlers)
    # These check user_data state and return early if not in that state
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_welcome_message_input
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_goodbye_message_input
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_caption_input
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_button_input
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_self_destruct_time_input
    ))
    
    # Register filter checker (for all text messages not handled above)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        check_filters
    ))
    
    application.add_handler(MessageHandler(
        filters.StatusUpdate.ALL,
        clean_service_messages
    ))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot is starting...")
    print("Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
