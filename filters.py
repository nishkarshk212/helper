"""
Filter system - Auto-reply to trigger words with custom content
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_or_create_group, update_group_setting
from font import to_monospace_uppercase
import json
import logging

logger = logging.getLogger(__name__)


async def handle_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new filter"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user is admin
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    
    if chat_member.status not in ['creator', 'administrator']:
        await update.message.reply_text("Only admins can add filters.")
        return
    
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "<b>How to add a filter:</b>\n\n"
            "1. Send the content you want as response (text/photo/video/sticker/etc.)\n"
            "2. Reply to that message with: <code>/filter trigger_word</code>\n\n"
            "<b>Examples:</b>\n"
            "• Send a sticker → Reply with <code>/filter awesome</code>\n"
            "• Send a photo → Reply with <code>/filter rules</code>\n"
            "• Send text → Reply with <code>/filter hello</code>",
            parse_mode='HTML'
        )
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Please reply to a message (text, photo, video, sticker, etc.) with:\n"
            f"<code>/filter {args[0]}</code>",
            parse_mode='HTML'
        )
        return
    
    trigger = args[0].lower()
    replied_msg = update.message.reply_to_message
    
    # Get settings
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    # Load existing filters
    try:
        filters = json.loads(settings.chat_filters)
    except:
        filters = {}
    
    filter_data = {}
    
    # Check for sticker
    if replied_msg.sticker:
        filter_data = {
            'type': 'sticker',
            'file_id': replied_msg.sticker.file_id,
            'content': ''
        }
    # Check for photo
    elif replied_msg.photo:
        filter_data = {
            'type': 'photo',
            'file_id': replied_msg.photo[-1].file_id,
            'content': replied_msg.caption or ''
        }
    # Check for video
    elif replied_msg.video:
        filter_data = {
            'type': 'video',
            'file_id': replied_msg.video.file_id,
            'content': replied_msg.caption or ''
        }
    # Check for document
    elif replied_msg.document:
        filter_data = {
            'type': 'document',
            'file_id': replied_msg.document.file_id,
            'content': replied_msg.caption or ''
        }
    # Check for animation (GIF)
    elif replied_msg.animation:
        filter_data = {
            'type': 'animation',
            'file_id': replied_msg.animation.file_id,
            'content': replied_msg.caption or ''
        }
    else:
        # Text reply
        filter_data = {
            'type': 'text',
            'content': replied_msg.text or '',
            'file_id': ''
        }
    
    # Save filter
    filters[trigger] = filter_data
    update_group_setting(chat_id, chat_filters=json.dumps(filters))
    
    await update.message.reply_text(
        f"✅ Filter added!\n\n"
        f"<b>Trigger:</b> <code>{trigger}</code>\n"
        f"<b>Type:</b> {filter_data['type'].capitalize()}\n\n"
        f"Now when someone says '{trigger}', I'll respond!",
        parse_mode='HTML'
    )


async def handle_filters_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all filters in the chat"""
    if not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    try:
        filters = json.loads(settings.chat_filters)
    except:
        filters = {}
    
    if not filters:
        await update.message.reply_text("No filters set in this chat yet!")
        return
    
    filter_list = "\n".join([f"• <code>{trigger}</code>" for trigger in sorted(filters.keys())])
    
    await update.message.reply_text(
        f"<b>📋 Chat Filters ({len(filters)}):</b>\n\n"
        f"{filter_list}\n\n"
        f"Use /stop <trigger> to remove a filter.",
        parse_mode='HTML'
    )


async def handle_stop_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a filter"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user is admin
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    
    if chat_member.status not in ['creator', 'administrator']:
        await update.message.reply_text("Only admins can remove filters.")
        return
    
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Which filter should I stop?\n"
            "Use: /stop <trigger>"
        )
        return
    
    trigger = args[0].lower()
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    try:
        filters = json.loads(settings.chat_filters)
    except:
        filters = {}
    
    if trigger not in filters:
        await update.message.reply_text(f"Filter '{trigger}' doesn't exist!")
        return
    
    del filters[trigger]
    update_group_setting(chat_id, chat_filters=json.dumps(filters))
    
    await update.message.reply_text(f"✅ Filter '{trigger}' has been removed!")


async def handle_stopall_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all filters"""
    if not update.effective_chat or not update.message:
        return
    
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    
    if chat_member.status != 'creator':
        await update.message.reply_text("Only the group creator can remove all filters.")
        return
    
    chat_id = update.effective_chat.id
    update_group_setting(chat_id, chat_filters='{}')
    
    await update.message.reply_text("✅ All filters have been removed!")


async def check_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if message triggers any filter"""
    if not update.effective_chat or not update.message or not update.message.text:
        logger.debug("check_filters: No message or text")
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    try:
        filters = json.loads(settings.chat_filters)
    except Exception as e:
        logger.error(f"Error loading filters: {e}")
        return
    
    logger.info(f"check_filters called for chat {chat_id}, filters count: {len(filters)}")
    
    if not filters:
        logger.debug("No filters configured")
        return
    
    message_text = update.message.text.lower().strip()
    logger.info(f"Checking filters for message: '{message_text}' in chat {chat_id}")
    logger.info(f"Available filters: {list(filters.keys())}")
    
    # Check each filter trigger
    triggered = False
    for trigger, filter_data in filters.items():
        # Check if trigger is in the message (case-insensitive)
        if trigger in message_text:
            logger.info(f"Filter triggered! Trigger: '{trigger}', Type: {filter_data['type']}")
            triggered = True
            # Send appropriate response based on type
            try:
                if filter_data['type'] == 'text':
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=filter_data['content'],
                        reply_to_message_id=update.message.message_id
                    )
                elif filter_data['type'] == 'sticker':
                    await context.bot.send_sticker(
                        chat_id=chat_id,
                        sticker=filter_data['file_id'],
                        reply_to_message_id=update.message.message_id
                    )
                elif filter_data['type'] == 'photo':
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=filter_data['file_id'],
                        caption=filter_data['content'] if filter_data['content'] else None,
                        reply_to_message_id=update.message.message_id
                    )
                elif filter_data['type'] == 'video':
                    await context.bot.send_video(
                        chat_id=chat_id,
                        video=filter_data['file_id'],
                        caption=filter_data['content'] if filter_data['content'] else None,
                        reply_to_message_id=update.message.message_id
                    )
                elif filter_data['type'] == 'document':
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=filter_data['file_id'],
                        caption=filter_data['content'] if filter_data['content'] else None,
                        reply_to_message_id=update.message.message_id
                    )
                elif filter_data['type'] == 'animation':
                    await context.bot.send_animation(
                        chat_id=chat_id,
                        animation=filter_data['file_id'],
                        caption=filter_data['content'] if filter_data['content'] else None,
                        reply_to_message_id=update.message.message_id
                    )
                logger.info(f"Filter response sent successfully")
            except Exception as e:
                logger.error(f"Error sending filter response: {e}", exc_info=True)
            
            # Only trigger once per message (first match)
            break
    
    if not triggered:
        logger.info(f"No filter matched for message: '{message_text}'")
    
    # Now handle self-destruct if enabled
    from handlers import handle_self_destruct_message
    await handle_self_destruct_message(update, context)
