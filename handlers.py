"""
Group management features: welcome messages, anti-spam, anti-flood, etc.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_or_create_group
from font import to_monospace_uppercase
import time
import json
import asyncio


# Track message counts for anti-flood
flood_tracker = {}


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new members joining the group"""
    if not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    if not settings.welcome_enabled:
        return
    
    for new_member in update.message.new_chat_members:
        # Don't welcome bots
        if new_member.is_bot:
            continue
        
        user_mention = new_member.mention_html()
        
        # Safely format the welcome message, replacing {user} placeholder
        try:
            welcome_msg = settings.welcome_message.replace('{user}', user_mention)
        except Exception as e:
            logger.error(f"Error formatting welcome message: {e}")
            welcome_msg = settings.welcome_message  # Use raw message if formatting fails
        
        # Parse buttons
        buttons = []
        try:
            buttons_data = json.loads(settings.welcome_buttons)
            for btn_data in buttons_data:
                buttons.append([InlineKeyboardButton(btn_data['text'], url=btn_data['url'])])
        except:
            pass
        
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        
        # Send message based on type
        try:
            if settings.welcome_type == 'photo' and settings.welcome_media_file_id:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=settings.welcome_media_file_id,
                    caption=welcome_msg,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            elif settings.welcome_type == 'video' and settings.welcome_media_file_id:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=settings.welcome_media_file_id,
                    caption=welcome_msg,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            elif settings.welcome_type == 'document' and settings.welcome_media_file_id:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=settings.welcome_media_file_id,
                    caption=welcome_msg,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            else:
                # Default to text
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=welcome_msg,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"Error sending welcome message: {e}")
            # Fallback to text message
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=welcome_msg,
                    parse_mode='HTML'
                )
            except:
                pass


async def handle_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle members leaving the group"""
    if not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    if not settings.goodbye_enabled:
        return
    
    left_member = update.message.left_chat_member
    
    # Don't say goodbye to bots
    if left_member.is_bot:
        return
    
    user_mention = left_member.mention_html()
    
    # Safely format the goodbye message, replacing {user} placeholder
    try:
        goodbye_msg = settings.goodbye_message.replace('{user}', user_mention)
    except Exception as e:
        logger.error(f"Error formatting goodbye message: {e}")
        goodbye_msg = settings.goodbye_message  # Use raw message if formatting fails
    
    # Parse buttons
    buttons = []
    try:
        buttons_data = json.loads(settings.goodbye_buttons)
        for btn_data in buttons_data:
            buttons.append([InlineKeyboardButton(btn_data['text'], url=btn_data['url'])])
    except:
        pass
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    # Send message based on type
    try:
        if settings.goodbye_type == 'photo' and settings.goodbye_media_file_id:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=settings.goodbye_media_file_id,
                caption=goodbye_msg,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        elif settings.goodbye_type == 'video' and settings.goodbye_media_file_id:
            await context.bot.send_video(
                chat_id=chat_id,
                video=settings.goodbye_media_file_id,
                caption=goodbye_msg,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        elif settings.goodbye_type == 'document' and settings.goodbye_media_file_id:
            await context.bot.send_document(
                chat_id=chat_id,
                document=settings.goodbye_media_file_id,
                caption=goodbye_msg,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            # Default to text
            await context.bot.send_message(
                chat_id=chat_id,
                text=goodbye_msg,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error sending goodbye message: {e}")
        # Fallback to text message
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=goodbye_msg,
                parse_mode='HTML'
            )
        except:
            pass


async def check_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check for spam and links"""
    if not update.effective_chat or not update.message or update.message.text is None:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    settings = get_or_create_group(chat_id)
    
    # Check if links are allowed
    if not settings.allowed_links:
        # Simple link detection
        text = update.message.text.lower()
        if any(keyword in text for keyword in ['http://', 'https://', 't.me/', 'telegram.me/']):
            if settings.anti_spam_enabled:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ Links are not allowed in this group.",
                    reply_to_message_id=update.message.message_id
                )
                return


async def check_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check for flooding (too many messages in short time)"""
    if not update.effective_chat or not update.message:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    settings = get_or_create_group(chat_id)
    
    if not settings.anti_flood_enabled:
        return
    
    current_time = time.time()
    
    # Initialize user tracking
    if chat_id not in flood_tracker:
        flood_tracker[chat_id] = {}
    
    if user_id not in flood_tracker[chat_id]:
        flood_tracker[chat_id][user_id] = []
    
    # Add current message timestamp
    flood_tracker[chat_id][user_id].append(current_time)
    
    # Remove old messages (older than 10 seconds)
    flood_tracker[chat_id][user_id] = [
        t for t in flood_tracker[chat_id][user_id] 
        if current_time - t < 10
    ]
    
    # Check if user exceeded flood limit
    if len(flood_tracker[chat_id][user_id]) > settings.flood_limit:
        try:
            await update.message.delete()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {update.effective_user.mention_html()} please slow down! "
                     f"Flood limit is {settings.flood_limit} messages per 10 seconds.",
                parse_mode='HTML'
            )
            
            # Reset counter
            flood_tracker[chat_id][user_id] = []
        except Exception as e:
            print(f"Error handling flood: {e}")


async def handle_self_destruct_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle self-destructing messages"""
    if not update.effective_chat or not update.message:
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    if not settings.self_destruct_enabled:
        return
    
    # Calculate total seconds
    total_seconds = (settings.self_destruct_hours * 3600 + 
                    settings.self_destruct_minutes * 60 + 
                    settings.self_destruct_seconds)
    
    # Don't delete if time is 0
    if total_seconds == 0:
        return
    
    message_id = update.message.message_id
    
    # Schedule message deletion
    async def delete_message():
        try:
            await asyncio.sleep(total_seconds)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    
    # Start the deletion task
    context.application.create_task(delete_message())


async def clean_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean service messages (join, leave, invite, voice chat)"""
    if not update.effective_chat or not update.message:
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    message_id = update.message.message_id
    should_delete = False
    
    # Check for new chat members (join messages)
    if update.message.new_chat_members and settings.clean_join_messages:
        should_delete = True
    
    # Check for left chat member (leave messages)
    elif update.message.left_chat_member and settings.clean_leave_messages:
        should_delete = True
    
    # Check for chat title/description/photo changes (invite/service messages)
    elif (update.message.new_chat_title or 
          update.message.new_chat_photo or 
          update.message.delete_chat_photo) and settings.clean_invite_messages:
        should_delete = True
    
    # Check for voice chat messages
    elif (hasattr(update.message, 'video_chat_started') and update.message.video_chat_started or
          hasattr(update.message, 'video_chat_ended') and update.message.video_chat_ended or
          hasattr(update.message, 'video_chat_participants_invited') and update.message.video_chat_participants_invited or
          hasattr(update.message, 'video_chat_scheduled') and update.message.video_chat_scheduled) and settings.clean_voice_chat_messages:
        should_delete = True
    
    # Delete the message if it matches enabled filters
    if should_delete:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Error deleting service message: {e}")
