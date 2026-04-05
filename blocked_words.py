"""
Blocked words feature - Delete messages containing blocked content
"""
from telegram import Update
from telegram.ext import ContextTypes
from database import get_or_create_group, update_group_setting
from font import to_monospace_uppercase
import json
import logging

logger = logging.getLogger(__name__)


async def handle_blockword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a word/phrase to the blocked list"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user provided a word
    if not context.args:
        return await update.message.reply_text(
            "❌ Usage: /blockword <word_or_phrase>\n\n"
            "Examples:\n"
            "• /blockword spam\n"
            "• /blockword bad word\n"
            "• /blockword https://"
        )
    
    # Get the word/phrase to block (join all args to support phrases)
    blocked_word = ' '.join(context.args).lower().strip()
    
    if not blocked_word:
        return await update.message.reply_text("❌ Please provide a valid word or phrase.")
    
    # Get current blocked words
    settings = get_or_create_group(update.effective_chat.id)
    try:
        blocked_words = json.loads(settings.blocked_words)
    except:
        blocked_words = []
    
    # Check if already blocked
    if blocked_word in blocked_words:
        return await update.message.reply_text(f"⚠️ '{blocked_word}' is already blocked.")
    
    # Add to list
    blocked_words.append(blocked_word)
    update_group_setting(update.effective_chat.id, blocked_words=json.dumps(blocked_words))
    
    await update.message.reply_text(
        f"✅ Blocked word added: '{blocked_word}'\n\n"
        f"Total blocked words: {len(blocked_words)}\n\n"
        f"Any message containing this word will be deleted immediately."
    )


async def handle_unblockword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a word/phrase from the blocked list"""
    if not update.effective_chat or not update.message:
        return
    
    if not context.args:
        return await update.message.reply_text(
            "❌ Usage: /unblockword <word_or_phrase>\n\n"
            "Use /blockedwords to see the list of blocked words."
        )
    
    # Get the word/phrase to unblock
    blocked_word = ' '.join(context.args).lower().strip()
    
    # Get current blocked words
    settings = get_or_create_group(update.effective_chat.id)
    try:
        blocked_words = json.loads(settings.blocked_words)
    except:
        blocked_words = []
    
    # Check if word exists
    if blocked_word not in blocked_words:
        return await update.message.reply_text(f"❌ '{blocked_word}' is not in the blocked list.")
    
    # Remove from list
    blocked_words.remove(blocked_word)
    update_group_setting(update.effective_chat.id, blocked_words=json.dumps(blocked_words))
    
    await update.message.reply_text(
        f"✅ Unblocked word: '{blocked_word}'\n\n"
        f"Remaining blocked words: {len(blocked_words)}"
    )


async def handle_blockedwords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all blocked words"""
    if not update.effective_chat or not update.message:
        return
    
    settings = get_or_create_group(update.effective_chat.id)
    try:
        blocked_words = json.loads(settings.blocked_words)
    except:
        blocked_words = []
    
    if not blocked_words:
        return await update.message.reply_text(
            "📝 No blocked words configured.\n\n"
            "Use /blockword <word> to add blocked words."
        )
    
    # Build message
    message = "<b>🚫 Blocked Words</b>\n\n"
    message += f"Total: {len(blocked_words)} word(s)\n\n"
    
    for i, word in enumerate(blocked_words, 1):
        message += f"{i}. <code>{word}</code>\n"
    
    message += "\n<i>Messages containing these words will be deleted automatically.</i>"
    
    await update.message.reply_text(message, parse_mode='HTML')


async def check_blocked_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if message contains blocked words and delete it"""
    if not update.effective_chat or not update.message:
        return
    
    # Skip commands
    if update.message.text and update.message.text.startswith('/'):
        return
    
    # Get blocked words
    settings = get_or_create_group(update.effective_chat.id)
    try:
        blocked_words = json.loads(settings.blocked_words)
    except:
        blocked_words = []
    
    # Check if any blocked word is in the message
    if blocked_words:
        # Get message text (including caption for media)
        message_text = ""
        if update.message.text:
            message_text = update.message.text.lower()
        elif update.message.caption:
            message_text = update.message.caption.lower()
        
        if message_text:
            for blocked_word in blocked_words:
                if blocked_word in message_text:
                    try:
                        # Delete the message
                        await update.message.delete()
                        
                        # Send warning (optional - can be removed if you don't want notifications)
                        warning = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"⚠️ Message deleted: Contains blocked word '{blocked_word}'",
                        )
                        
                        # Auto-delete warning after 5 seconds
                        import asyncio
                        asyncio.create_task(auto_delete_warning(warning, context))
                        
                    except Exception as e:
                        print(f"Error deleting blocked message: {e}")
                    break
    
    # Now check filters (so both blocked words AND filters work)
    logger.info("Calling check_filters from blocked_words handler")
    from filters import check_filters
    await check_filters(update, context)


async def auto_delete_warning(message, context):
    """Delete warning message after 5 seconds"""
    import asyncio
    await asyncio.sleep(5)
    try:
        await message.delete()
    except:
        pass
