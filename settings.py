"""
Settings panel handlers for the Telegram bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_or_create_group, update_group_setting
from font import to_monospace_uppercase
import json
import logging

logger = logging.getLogger(__name__)


async def show_settings_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the main settings panel"""
    if not update.effective_chat or update.effective_chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(to_monospace_uppercase("This command can only be used in groups."))
        return
    
    # Check if user is admin
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id, 
        update.effective_user.id
    )
    
    if chat_member.status not in ['creator', 'administrator']:
        await update.message.reply_text(to_monospace_uppercase("Only admins can access settings."))
        return
    
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if settings.welcome_enabled else '❌'} Welcome Messages",
                callback_data="welcome_settings"
            ),
            InlineKeyboardButton(
                f"{'✅' if settings.goodbye_enabled else '❌'} Goodbye Messages",
                callback_data="goodbye_settings"
            )
        ],
        [
            InlineKeyboardButton("💥 Self-Destruct Messages", callback_data="self_destruct_settings")
        ],
        [
            InlineKeyboardButton("🧹 Clean Service Messages", callback_data="clean_service_settings")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close_settings")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = to_monospace_uppercase(
        f"⚙️ Group Settings Panel\n\n"
        f"Current Settings:\n"
        f"• Welcome Messages: {'Enabled' if settings.welcome_enabled else 'Disabled'}\n"
        f"• Goodbye Messages: {'Enabled' if settings.goodbye_enabled else 'Disabled'}\n"
        f"• Self-Destruct: {'Enabled' if settings.self_destruct_enabled else 'Disabled'}\n"
        f"• Clean Service Messages: {'Enabled' if any([settings.clean_join_messages, settings.clean_leave_messages, settings.clean_invite_messages, settings.clean_voice_chat_messages]) else 'Disabled'}\n\n"
        f"Click on Welcome or Goodbye to configure messages, media, and buttons."
    )
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from settings panel"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    
    # Check if user is admin
    chat_member = await context.bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['creator', 'administrator']:
        await query.edit_message_text(to_monospace_uppercase("Only admins can change settings."))
        return
    
    settings = get_or_create_group(chat_id)
    action = query.data
    
    if action == "welcome_settings":
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.welcome_enabled else '❌'} Enable/Disable Welcome",
                    callback_data="toggle_welcome"
                )
            ],
            [
                InlineKeyboardButton("📝 Edit Welcome Message", callback_data="edit_welcome_msg")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg_type = settings.welcome_type.capitalize()
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.welcome_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        
        await query.edit_message_text(
            to_monospace_uppercase(
                f"Welcome Message Settings\n\n"
                f"Status: {'Enabled' if settings.welcome_enabled else 'Disabled'}\n"
                f"Type: {msg_type}\n"
                f"Buttons: {buttons_count} button(s)\n\n"
                f"Enable/disable welcome messages or edit the message content, media, and buttons."
            ),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "goodbye_settings":
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.goodbye_enabled else '❌'} Enable/Disable Goodbye",
                    callback_data="toggle_goodbye"
                )
            ],
            [
                InlineKeyboardButton("👋 Edit Goodbye Message", callback_data="edit_goodbye_msg")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg_type = settings.goodbye_type.capitalize()
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.goodbye_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        
        await query.edit_message_text(
            to_monospace_uppercase(
                f"Goodbye Message Settings\n\n"
                f"Status: {'Enabled' if settings.goodbye_enabled else 'Disabled'}\n"
                f"Type: {msg_type}\n"
                f"Buttons: {buttons_count} button(s)\n\n"
                f"Enable/disable goodbye messages or edit the message content, media, and buttons."
            ),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    if action == "toggle_welcome":
        new_state = not settings.welcome_enabled
        update_group_setting(chat_id, welcome_enabled=new_state)
        
        # Refresh the welcome settings panel
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Enable/Disable Welcome",
                    callback_data="toggle_welcome"
                )
            ],
            [
                InlineKeyboardButton("📝 Edit Welcome Message", callback_data="edit_welcome_msg")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg_type = settings.welcome_type.capitalize()
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.welcome_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        
        await query.edit_message_text(
            f"<b>Welcome Message Settings</b>\n\n"
            f"Welcome messages {'enabled' if new_state else 'disabled'}.\n\n"
            f"<b>Type:</b> {msg_type}\n"
            f"<b>Buttons:</b> {buttons_count} button(s)",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "toggle_goodbye":
        new_state = not settings.goodbye_enabled
        update_group_setting(chat_id, goodbye_enabled=new_state)
        
        # Refresh the welcome/goodbye settings panel
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Enable/Disable Goodbye",
                    callback_data="toggle_goodbye"
                )
            ],
            [
                InlineKeyboardButton("👋 Edit Goodbye Message", callback_data="edit_goodbye_msg")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg_type = settings.goodbye_type.capitalize()
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.goodbye_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        
        await query.edit_message_text(
            f"<b>Goodbye Message Settings</b>\n\n"
            f"Goodbye messages {'enabled' if new_state else 'disabled'}.\n\n"
            f"<b>Type:</b> {msg_type}\n"
            f"<b>Buttons:</b> {buttons_count} button(s)",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "edit_welcome_msg":
        keyboard = [
            [InlineKeyboardButton("Text", callback_data="welcome_type_text"),
             InlineKeyboardButton("Photo", callback_data="welcome_type_photo")],
            [InlineKeyboardButton("Video", callback_data="welcome_type_video"),
             InlineKeyboardButton("Document", callback_data="welcome_type_document")],
            [InlineKeyboardButton("🔘 Configure Buttons", callback_data="configure_welcome_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="welcome_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        current_type = settings.welcome_type.capitalize()
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.welcome_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        await query.edit_message_text(
            f"<b>Welcome Message Configuration</b>\n\n"
            f"<b>Current type:</b> {current_type}\n"
            f"<b>Current buttons:</b> {buttons_count} button(s)\n\n"
            f"Select message type or configure buttons:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "edit_goodbye_msg":
        keyboard = [
            [InlineKeyboardButton("Text", callback_data="goodbye_type_text"),
             InlineKeyboardButton("Photo", callback_data="goodbye_type_photo")],
            [InlineKeyboardButton("Video", callback_data="goodbye_type_video"),
             InlineKeyboardButton("Document", callback_data="goodbye_type_document")],
            [InlineKeyboardButton("🔘 Configure Buttons", callback_data="configure_goodbye_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="goodbye_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        current_type = settings.goodbye_type.capitalize()
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.goodbye_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        await query.edit_message_text(
            f"<b>Goodbye Message Configuration</b>\n\n"
            f"<b>Current type:</b> {current_type}\n"
            f"<b>Current buttons:</b> {buttons_count} button(s)\n\n"
            f"Select message type or configure buttons:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "configure_welcome_buttons":
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.welcome_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        
        keyboard = [
            [InlineKeyboardButton("Add/Edit Buttons", callback_data="add_welcome_buttons")],
            [InlineKeyboardButton("Remove All Buttons", callback_data="remove_welcome_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="edit_welcome_msg")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>Welcome Message Buttons</b>\n\n"
            f"<b>Current buttons:</b> {buttons_count}\n\n"
            f"You can add, edit, or remove inline buttons for welcome messages.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "configure_goodbye_buttons":
        buttons_count = 0
        try:
            buttons_data = json.loads(settings.goodbye_buttons)
            buttons_count = len(buttons_data)
        except:
            pass
        
        keyboard = [
            [InlineKeyboardButton("Add/Edit Buttons", callback_data="add_goodbye_buttons")],
            [InlineKeyboardButton("Remove All Buttons", callback_data="remove_goodbye_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="edit_goodbye_msg")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>Goodbye Message Buttons</b>\n\n"
            f"<b>Current buttons:</b> {buttons_count}\n\n"
            f"You can add, edit, or remove inline buttons for goodbye messages.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "remove_welcome_buttons":
        update_group_setting(chat_id, welcome_buttons="[]")
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_welcome_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="configure_welcome_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ All welcome message buttons removed!\n\n"
            f"Would you like to add new buttons?",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "remove_goodbye_buttons":
        update_group_setting(chat_id, goodbye_buttons="[]")
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_goodbye_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="configure_goodbye_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ All goodbye message buttons removed!\n\n"
            f"Would you like to add new buttons?",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action.startswith("welcome_type_"):
        msg_type = action.split("_")[-1]
        update_group_setting(chat_id, welcome_type=msg_type)
        
        if msg_type == "text":
            await query.edit_message_text(
                to_monospace_uppercase(
                    "Please send the new welcome message text.\n"
                    "Use {user} to mention the new member.\n"
                    "Send /cancel to abort."
                ),
                reply_markup=None
            )
            context.user_data['waiting_for_welcome_msg'] = True
            logger.info(f"Set waiting_for_welcome_msg=True for user {query.from_user.id}")
        else:
            media_names = {
                'photo': 'photo/image',
                'video': 'video',
                'document': 'document/file'
            }
            await query.edit_message_text(
                f"Please send the {media_names.get(msg_type, 'media')} for welcome message.\n"
                f"After sending the media, send the caption text (or /skip for no caption).\n"
                f"Use {{user}} to mention the new member.\n"
                f"Send /cancel to abort.",
                reply_markup=None
            )
            context.user_data['waiting_for_welcome_media'] = True
            context.user_data['welcome_media_type'] = msg_type
    
    elif action.startswith("goodbye_type_"):
        msg_type = action.split("_")[-1]
        update_group_setting(chat_id, goodbye_type=msg_type)
        
        if msg_type == "text":
            await query.edit_message_text(
                "Please send the new goodbye message text.\n"
                "Use {user} to mention the leaving member.\n"
                "Send /cancel to abort.",
                reply_markup=None
            )
            context.user_data['waiting_for_goodbye_msg'] = True
        else:
            media_names = {
                'photo': 'photo/image',
                'video': 'video',
                'document': 'document/file'
            }
            await query.edit_message_text(
                f"Please send the {media_names.get(msg_type, 'media')} for goodbye message.\n"
                f"After sending the media, send the caption text (or /skip for no caption).\n"
                f"Use {{user}} to mention the leaving member.\n"
                f"Send /cancel to abort.",
                reply_markup=None
            )
            context.user_data['waiting_for_goodbye_media'] = True
            context.user_data['goodbye_media_type'] = msg_type
    
    elif action == "self_destruct_settings":
        total_seconds = (settings.self_destruct_hours * 3600 + 
                        settings.self_destruct_minutes * 60 + 
                        settings.self_destruct_seconds)
        
        if total_seconds == 0:
            time_str = "Disabled"
        else:
            parts = []
            if settings.self_destruct_hours > 0:
                parts.append(f"{settings.self_destruct_hours}h")
            if settings.self_destruct_minutes > 0:
                parts.append(f"{settings.self_destruct_minutes}m")
            if settings.self_destruct_seconds > 0:
                parts.append(f"{settings.self_destruct_seconds}s")
            time_str = " ".join(parts)
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.self_destruct_enabled else '❌'} Enable/Disable",
                    callback_data="toggle_self_destruct"
                )
            ],
            [
                InlineKeyboardButton("Set Hours", callback_data="set_destruct_hours"),
                InlineKeyboardButton("Set Minutes", callback_data="set_destruct_minutes")
            ],
            [
                InlineKeyboardButton("Set Seconds", callback_data="set_destruct_seconds")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>💥 Self-Destruct Messages Settings</b>\n\n"
            f"<b>Status:</b> {'Enabled' if settings.self_destruct_enabled else 'Disabled'}\n"
            f"<b>Delete after:</b> {time_str}\n\n"
            f"<b>⚠️ IMPORTANT:</b> When enabled, <b>ALL messages</b> from <b>ALL users</b> "
            f"(including group owner, admins, and members) will be automatically deleted after the specified time.\n\n"
            f"<i>Note: Minimum 5 seconds recommended for proper functionality.</i>",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "toggle_self_destruct":
        new_state = not settings.self_destruct_enabled
        update_group_setting(chat_id, self_destruct_enabled=new_state)
        
        # Refresh the self-destruct settings panel
        total_seconds = (settings.self_destruct_hours * 3600 + 
                        settings.self_destruct_minutes * 60 + 
                        settings.self_destruct_seconds)
        
        if total_seconds == 0:
            time_str = "Disabled"
        else:
            parts = []
            if settings.self_destruct_hours > 0:
                parts.append(f"{settings.self_destruct_hours}h")
            if settings.self_destruct_minutes > 0:
                parts.append(f"{settings.self_destruct_minutes}m")
            if settings.self_destruct_seconds > 0:
                parts.append(f"{settings.self_destruct_seconds}s")
            time_str = " ".join(parts)
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Enable/Disable",
                    callback_data="toggle_self_destruct"
                )
            ],
            [
                InlineKeyboardButton("⏱️ Set Delete Time", callback_data="set_destruct_time")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            to_monospace_uppercase(
                f"💥 Self-Destruct Messages Settings\n\n"
                f"Self-destruct messages {'enabled' if new_state else 'disabled'}.\n\n"
                f"Current delete time: {time_str}\n\n"
                f"⚠️ WARNING: This will delete ALL messages from EVERYONE "
                f"(owner, admins & members) after the set time. No exceptions!"
            ),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "set_destruct_time":
        # Show time setting panel with +/- buttons
        hours = settings.destruct_hours
        minutes = settings.destruct_minutes
        seconds = settings.destruct_seconds
        
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data=f"destruct_hours_-1"),
                InlineKeyboardButton(f"Hours: {hours}", callback_data="noop"),
                InlineKeyboardButton("➕", callback_data=f"destruct_hours_+1")
            ],
            [
                InlineKeyboardButton("➖", callback_data=f"destruct_minutes_-1"),
                InlineKeyboardButton(f"Minutes: {minutes}", callback_data="noop"),
                InlineKeyboardButton("➕", callback_data=f"destruct_minutes_+1")
            ],
            [
                InlineKeyboardButton("➖", callback_data=f"destruct_seconds_-5"),
                InlineKeyboardButton(f"Seconds: {seconds}", callback_data="noop"),
                InlineKeyboardButton("➕", callback_data=f"destruct_seconds_+5")
            ],
            [
                InlineKeyboardButton("✅ Done", callback_data="destruct_time_done"),
                InlineKeyboardButton("⬅️ Back", callback_data="self_destruct_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            to_monospace_uppercase(
                f"⏱️ Set Self-Destruct Time\n\n"
                f"Use + / - buttons to adjust:\n\n"
                f"Minimum recommended: 5 seconds\n"
                f"Maximum: 23 hours, 59 minutes, 59 seconds"
            ),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "clean_service_settings":
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_join_messages else '❌'} Clean Join Messages",
                    callback_data="toggle_clean_join"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_leave_messages else '❌'} Clean Leave Messages",
                    callback_data="toggle_clean_leave"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_invite_messages else '❌'} Clean Invite Messages",
                    callback_data="toggle_clean_invite"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_voice_chat_messages else '❌'} Clean Voice Chat Messages",
                    callback_data="toggle_clean_voice_chat"
                )
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>🧹 Clean Service Messages Settings</b>\n\n"
            f"Automatically delete service messages to keep your chat clean.\n\n"
            f"<b>Current Settings:</b>\n"
            f"• Join Messages: {'Enabled' if settings.clean_join_messages else 'Disabled'}\n"
            f"• Leave Messages: {'Enabled' if settings.clean_leave_messages else 'Disabled'}\n"
            f"• Invite Messages: {'Enabled' if settings.clean_invite_messages else 'Disabled'}\n"
            f"• Voice Chat Messages: {'Enabled' if settings.clean_voice_chat_messages else 'Disabled'}\n\n"
            f"Toggle each option to enable/disable cleaning.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "toggle_clean_join":
        new_state = not settings.clean_join_messages
        update_group_setting(chat_id, clean_join_messages=new_state)
        # Refresh the clean service settings panel
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Clean Join Messages",
                    callback_data="toggle_clean_join"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_leave_messages else '❌'} Clean Leave Messages",
                    callback_data="toggle_clean_leave"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_invite_messages else '❌'} Clean Invite Messages",
                    callback_data="toggle_clean_invite"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_voice_chat_messages else '❌'} Clean Voice Chat Messages",
                    callback_data="toggle_clean_voice_chat"
                )
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>🧹 Clean Service Messages Settings</b>\n\n"
            f"Join messages cleaning {'enabled' if new_state else 'disabled'}.\n\n"
            f"<b>Current Settings:</b>\n"
            f"• Join Messages: {'Enabled' if new_state else 'Disabled'}\n"
            f"• Leave Messages: {'Enabled' if settings.clean_leave_messages else 'Disabled'}\n"
            f"• Invite Messages: {'Enabled' if settings.clean_invite_messages else 'Disabled'}\n"
            f"• Voice Chat Messages: {'Enabled' if settings.clean_voice_chat_messages else 'Disabled'}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "toggle_clean_leave":
        new_state = not settings.clean_leave_messages
        update_group_setting(chat_id, clean_leave_messages=new_state)
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_join_messages else '❌'} Clean Join Messages",
                    callback_data="toggle_clean_join"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Clean Leave Messages",
                    callback_data="toggle_clean_leave"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_invite_messages else '❌'} Clean Invite Messages",
                    callback_data="toggle_clean_invite"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_voice_chat_messages else '❌'} Clean Voice Chat Messages",
                    callback_data="toggle_clean_voice_chat"
                )
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>🧹 Clean Service Messages Settings</b>\n\n"
            f"Leave messages cleaning {'enabled' if new_state else 'disabled'}.\n\n"
            f"<b>Current Settings:</b>\n"
            f"• Join Messages: {'Enabled' if settings.clean_join_messages else 'Disabled'}\n"
            f"• Leave Messages: {'Enabled' if new_state else 'Disabled'}\n"
            f"• Invite Messages: {'Enabled' if settings.clean_invite_messages else 'Disabled'}\n"
            f"• Voice Chat Messages: {'Enabled' if settings.clean_voice_chat_messages else 'Disabled'}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "toggle_clean_invite":
        new_state = not settings.clean_invite_messages
        update_group_setting(chat_id, clean_invite_messages=new_state)
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_join_messages else '❌'} Clean Join Messages",
                    callback_data="toggle_clean_join"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_leave_messages else '❌'} Clean Leave Messages",
                    callback_data="toggle_clean_leave"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Clean Invite Messages",
                    callback_data="toggle_clean_invite"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_voice_chat_messages else '❌'} Clean Voice Chat Messages",
                    callback_data="toggle_clean_voice_chat"
                )
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>🧹 Clean Service Messages Settings</b>\n\n"
            f"Invite messages cleaning {'enabled' if new_state else 'disabled'}.\n\n"
            f"<b>Current Settings:</b>\n"
            f"• Join Messages: {'Enabled' if settings.clean_join_messages else 'Disabled'}\n"
            f"• Leave Messages: {'Enabled' if settings.clean_leave_messages else 'Disabled'}\n"
            f"• Invite Messages: {'Enabled' if new_state else 'Disabled'}\n"
            f"• Voice Chat Messages: {'Enabled' if settings.clean_voice_chat_messages else 'Disabled'}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif action == "toggle_clean_voice_chat":
        new_state = not settings.clean_voice_chat_messages
        update_group_setting(chat_id, clean_voice_chat_messages=new_state)
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_join_messages else '❌'} Clean Join Messages",
                    callback_data="toggle_clean_join"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_leave_messages else '❌'} Clean Leave Messages",
                    callback_data="toggle_clean_leave"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.clean_invite_messages else '❌'} Clean Invite Messages",
                    callback_data="toggle_clean_invite"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if new_state else '❌'} Clean Voice Chat Messages",
                    callback_data="toggle_clean_voice_chat"
                )
            ],
            [
                InlineKeyboardButton("⬅️ Back to Settings", callback_data="back_to_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"<b>🧹 Clean Service Messages Settings</b>\n\n"
            f"Voice chat messages cleaning {'enabled' if new_state else 'disabled'}.\n\n"
            f"<b>Current Settings:</b>\n"
            f"• Join Messages: {'Enabled' if settings.clean_join_messages else 'Disabled'}\n"
            f"• Leave Messages: {'Enabled' if settings.clean_leave_messages else 'Disabled'}\n"
            f"• Invite Messages: {'Enabled' if settings.clean_invite_messages else 'Disabled'}\n"
            f"• Voice Chat Messages: {'Enabled' if new_state else 'Disabled'}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    # Handle destruct time +/- buttons
    elif action.startswith("destruct_hours_"):
        change = int(action.split("_")[-1])
        new_hours = max(0, min(23, settings.destruct_hours + change))
        update_group_setting(chat_id, destruct_hours=new_hours)
        await _show_destruct_time_panel(query, context, chat_id)
    
    elif action.startswith("destruct_minutes_"):
        change = int(action.split("_")[-1])
        new_minutes = max(0, min(59, settings.destruct_minutes + change))
        update_group_setting(chat_id, destruct_minutes=new_minutes)
        await _show_destruct_time_panel(query, context, chat_id)
    
    elif action.startswith("destruct_seconds_"):
        change = int(action.split("_")[-1])
        new_seconds = max(5, min(59, settings.destruct_seconds + change))
        update_group_setting(chat_id, destruct_seconds=new_seconds)
        await _show_destruct_time_panel(query, context, chat_id)
    
    elif action == "destruct_time_done":
        await query.edit_message_text(
            to_monospace_uppercase(
                f"✅ Self-destruct time updated!\n\n"
                f"Messages will be deleted after:\n"
                f"{settings.destruct_hours}h {settings.destruct_minutes}m {settings.destruct_seconds}s"
            ),
            reply_markup=None
        )
    
    elif action == "back_to_settings":
        await show_settings_panel_from_callback(query, context, settings)
    
    elif action == "close_settings":
        await query.edit_message_text("Settings panel closed.")


async def show_settings_panel_from_callback(query, context, settings):
    """Show settings panel from a callback query"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if settings.welcome_enabled else '❌'} Welcome Messages",
                callback_data="welcome_settings"
            ),
            InlineKeyboardButton(
                f"{'✅' if settings.goodbye_enabled else '❌'} Goodbye Messages",
                callback_data="goodbye_settings"
            )
        ],
        [
            InlineKeyboardButton("💥 Self-Destruct Messages", callback_data="self_destruct_settings")
        ],
        [
            InlineKeyboardButton("🧹 Clean Service Messages", callback_data="clean_service_settings")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close_settings")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"⚙️ <b>Group Settings Panel</b>\n\n"
        f"<b>Current Settings:</b>\n"
        f"• Welcome Messages: {'Enabled' if settings.welcome_enabled else 'Disabled'}\n"
        f"• Goodbye Messages: {'Enabled' if settings.goodbye_enabled else 'Disabled'}\n"
        f"• Self-Destruct: {'Enabled' if settings.self_destruct_enabled else 'Disabled'}\n"
        f"• Clean Service Messages: {'Enabled' if any([settings.clean_join_messages, settings.clean_leave_messages, settings.clean_invite_messages, settings.clean_voice_chat_messages]) else 'Disabled'}\n\n"
        f"Click on Welcome or Goodbye to configure messages, media, and buttons."
    )
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def _show_destruct_time_panel(query, context, chat_id):
    """Show the destruct time setting panel with current values"""
    settings = get_or_create_group(chat_id)
    hours = settings.destruct_hours
    minutes = settings.destruct_minutes
    seconds = settings.destruct_seconds
    
    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data=f"destruct_hours_-1"),
            InlineKeyboardButton(f"Hours: {hours}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"destruct_hours_+1")
        ],
        [
            InlineKeyboardButton("➖", callback_data=f"destruct_minutes_-1"),
            InlineKeyboardButton(f"Minutes: {minutes}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"destruct_minutes_+1")
        ],
        [
            InlineKeyboardButton("➖", callback_data=f"destruct_seconds_-5"),
            InlineKeyboardButton(f"Seconds: {seconds}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"destruct_seconds_+5")
        ],
        [
            InlineKeyboardButton("✅ Done", callback_data="destruct_time_done"),
            InlineKeyboardButton("⬅️ Back", callback_data="self_destruct_settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        to_monospace_uppercase(
            f"⏱️ Set Self-Destruct Time\n\n"
            f"Use + / - buttons to adjust:\n\n"
            f"Minimum recommended: 5 seconds\n"
            f"Maximum: 23 hours, 59 minutes, 59 seconds"
        ),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def handle_welcome_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new welcome message input (text)"""
    is_waiting = context.user_data.get('waiting_for_welcome_msg')
    logger.info(f"handle_welcome_message_input called, waiting={is_waiting}, text={update.message.text if update.message else 'None'}")
    
    if not is_waiting:
        return
    
    try:
        new_message = update.message.text
        logger.info(f"Processing welcome message: {new_message[:50]}...")
        
        if new_message == "/cancel":
            await update.message.reply_text(to_monospace_uppercase("Cancelled."))
            context.user_data['waiting_for_welcome_msg'] = False
            return
        
        chat_id = update.effective_chat.id
        update_group_setting(chat_id, welcome_message=new_message)
        
        # Ask about buttons
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_welcome_buttons"),
             InlineKeyboardButton("Skip", callback_data="skip_welcome_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            to_monospace_uppercase(
                "Welcome message text saved!\n\n"
                "Would you like to add inline buttons?"
            ),
            reply_markup=reply_markup
        )
        context.user_data['waiting_for_welcome_msg'] = False
    except Exception as e:
        logger.error(f"Error in handle_welcome_message_input: {e}", exc_info=True)
        await update.message.reply_text(
            to_monospace_uppercase("❌ An error occurred while saving the welcome message. Please try again.")
        )
        context.user_data['waiting_for_welcome_msg'] = False


async def handle_goodbye_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new goodbye message input (text)"""
    if not context.user_data.get('waiting_for_goodbye_msg'):
        return
    
    try:
        new_message = update.message.text
        
        if new_message == "/cancel":
            await update.message.reply_text(to_monospace_uppercase("Cancelled."))
            context.user_data['waiting_for_goodbye_msg'] = False
            return
        
        chat_id = update.effective_chat.id
        update_group_setting(chat_id, goodbye_message=new_message)
        
        # Ask about buttons
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_goodbye_buttons"),
             InlineKeyboardButton("Skip", callback_data="skip_goodbye_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            to_monospace_uppercase(
                "Goodbye message text saved!\n\n"
                "Would you like to add inline buttons?"
            ),
            reply_markup=reply_markup
        )
        context.user_data['waiting_for_goodbye_msg'] = False
    except Exception as e:
        logger.error(f"Error in handle_goodbye_message_input: {e}", exc_info=True)
        await update.message.reply_text(
            to_monospace_uppercase("❌ An error occurred while saving the goodbye message. Please try again.")
        )
        context.user_data['waiting_for_goodbye_msg'] = False


async def handle_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle media messages for welcome/goodbye configuration"""
    chat_id = update.effective_chat.id
    
    # Handle welcome media
    if context.user_data.get('waiting_for_welcome_media'):
        media_type = context.user_data.get('welcome_media_type', 'photo')
        
        # Get file_id based on media type
        file_id = None
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
        elif update.message.video:
            file_id = update.message.video.file_id
        elif update.message.document:
            file_id = update.message.document.file_id
        
        if file_id:
            update_group_setting(chat_id, welcome_media_file_id=file_id)
            context.user_data['welcome_media_received'] = True
            
            await update.message.reply_text(
                "Media received! Now send the caption text (or /skip for no caption).\n"
                "Use {user} to mention the new member."
            )
            context.user_data['waiting_for_welcome_caption'] = True
            context.user_data['waiting_for_welcome_media'] = False
        else:
            await update.message.reply_text("Please send a valid media file.")
    
    # Handle goodbye media
    elif context.user_data.get('waiting_for_goodbye_media'):
        media_type = context.user_data.get('goodbye_media_type', 'photo')
        
        # Get file_id based on media type
        file_id = None
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
        elif update.message.video:
            file_id = update.message.video.file_id
        elif update.message.document:
            file_id = update.message.document.file_id
        
        if file_id:
            update_group_setting(chat_id, goodbye_media_file_id=file_id)
            context.user_data['goodbye_media_received'] = True
            
            await update.message.reply_text(
                "Media received! Now send the caption text (or /skip for no caption).\n"
                "Use {user} to mention the leaving member."
            )
            context.user_data['waiting_for_goodbye_caption'] = True
            context.user_data['waiting_for_goodbye_media'] = False


async def handle_caption_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle caption input for media messages"""
    chat_id = update.effective_chat.id
    
    # Handle welcome caption
    if context.user_data.get('waiting_for_welcome_caption'):
        caption = update.message.text
        
        if caption == "/skip":
            caption = ""
        elif caption == "/cancel":
            await update.message.reply_text("Cancelled.")
            context.user_data['waiting_for_welcome_caption'] = False
            return
        
        update_group_setting(chat_id, welcome_message=caption)
        
        # Ask about buttons
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_welcome_buttons"),
             InlineKeyboardButton("Skip", callback_data="skip_welcome_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Caption saved!\n\nWould you like to add inline buttons?",
            reply_markup=reply_markup
        )
        context.user_data['waiting_for_welcome_caption'] = False
    
    # Handle goodbye caption
    elif context.user_data.get('waiting_for_goodbye_caption'):
        caption = update.message.text
        
        if caption == "/skip":
            caption = ""
        elif caption == "/cancel":
            await update.message.reply_text("Cancelled.")
            context.user_data['waiting_for_goodbye_caption'] = False
            return
        
        update_group_setting(chat_id, goodbye_message=caption)
        
        # Ask about buttons
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_goodbye_buttons"),
             InlineKeyboardButton("Skip", callback_data="skip_goodbye_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Caption saved!\n\nWould you like to add inline buttons?",
            reply_markup=reply_markup
        )
        context.user_data['waiting_for_goodbye_caption'] = False


async def handle_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button configuration callbacks"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    action = query.data
    
    # Check if user is admin
    chat_member = await context.bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['creator', 'administrator']:
        await query.edit_message_text("Only admins can configure buttons.")
        return
    
    settings = get_or_create_group(chat_id)
    
    if action == "add_welcome_buttons":
        await query.edit_message_text(
            "<b>Inline Button Configuration for Welcome Message</b>\n\n"
            "Send buttons in this format (one per line):\n"
            "<code>Button Text - URL</code>\n\n"
            "Example:\n"
            "<code>Channel - https://t.me/channel\nGroup Rules - https://example.com/rules</code>\n\n"
            "Send /cancel to abort or /skip to continue without buttons.",
            parse_mode='HTML',
            reply_markup=None
        )
        context.user_data['waiting_for_welcome_buttons'] = True
        context.user_data['return_to'] = 'configure_welcome_buttons'
    
    elif action == "skip_welcome_buttons":
        update_group_setting(chat_id, welcome_buttons="[]")
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_welcome_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="configure_welcome_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "✅ Welcome message configuration complete!\n\n"
            "No buttons will be added.\n\n"
            "Would you like to add buttons now?",
            reply_markup=reply_markup
        )
        context.user_data.pop('waiting_for_welcome_buttons', None)
    
    elif action == "add_goodbye_buttons":
        await query.edit_message_text(
            "<b>Inline Button Configuration for Goodbye Message</b>\n\n"
            "Send buttons in this format (one per line):\n"
            "<code>Button Text - URL</code>\n\n"
            "Example:\n"
            "<code>Rejoin - https://t.me/group\nSupport - https://t.me/support</code>\n\n"
            "Send /cancel to abort or /skip to continue without buttons.",
            parse_mode='HTML',
            reply_markup=None
        )
        context.user_data['waiting_for_goodbye_buttons'] = True
        context.user_data['return_to'] = 'configure_goodbye_buttons'
    
    elif action == "skip_goodbye_buttons":
        update_group_setting(chat_id, goodbye_buttons="[]")
        keyboard = [
            [InlineKeyboardButton("Add Buttons", callback_data="add_goodbye_buttons")],
            [InlineKeyboardButton("⬅️ Back", callback_data="configure_goodbye_buttons")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "✅ Goodbye message configuration complete!\n\n"
            "No buttons will be added.\n\n"
            "Would you like to add buttons now?",
            reply_markup=reply_markup
        )
        context.user_data.pop('waiting_for_goodbye_buttons', None)


async def handle_button_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button configuration input"""
    chat_id = update.effective_chat.id
    
    # Handle welcome buttons
    if context.user_data.get('waiting_for_welcome_buttons'):
        text = update.message.text
        
        if text == "/cancel":
            await update.message.reply_text("Cancelled button configuration.")
            context.user_data['waiting_for_welcome_buttons'] = False
            return
        
        if text == "/skip":
            update_group_setting(chat_id, welcome_buttons="[]")
            await update.message.reply_text("✅ Welcome message configuration complete!\nNo buttons added.")
            context.user_data['waiting_for_welcome_buttons'] = False
            return
        
        # Parse buttons
        buttons = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if ' - ' in line:
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    buttons.append({"text": btn_text, "url": btn_url})
        
        if buttons:
            buttons_json = json.dumps(buttons)
            update_group_setting(chat_id, welcome_buttons=buttons_json)
            keyboard = [
                [InlineKeyboardButton("Add More Buttons", callback_data="add_welcome_buttons")],
                [InlineKeyboardButton("✅ Done", callback_data="configure_welcome_buttons")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"✅ Welcome message buttons saved!\n\n"
                f"Added {len(buttons)} button(s).\n\n"
                f"What would you like to do next?",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("Try Again", callback_data="add_welcome_buttons")],
                [InlineKeyboardButton("⬅️ Back", callback_data="configure_welcome_buttons")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "⚠️ No valid buttons found. Please use the format:\n"
                "<code>Button Text - URL</code>\n\n"
                "Would you like to try again?",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return
        
        context.user_data['waiting_for_welcome_buttons'] = False
    
    # Handle goodbye buttons
    elif context.user_data.get('waiting_for_goodbye_buttons'):
        text = update.message.text
        
        if text == "/cancel":
            await update.message.reply_text("Cancelled button configuration.")
            context.user_data['waiting_for_goodbye_buttons'] = False
            return
        
        if text == "/skip":
            update_group_setting(chat_id, goodbye_buttons="[]")
            await update.message.reply_text("✅ Goodbye message configuration complete!\nNo buttons added.")
            context.user_data['waiting_for_goodbye_buttons'] = False
            return
        
        # Parse buttons
        buttons = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if ' - ' in line:
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    buttons.append({"text": btn_text, "url": btn_url})
        
        if buttons:
            buttons_json = json.dumps(buttons)
            update_group_setting(chat_id, goodbye_buttons=buttons_json)
            keyboard = [
                [InlineKeyboardButton("Add More Buttons", callback_data="add_goodbye_buttons")],
                [InlineKeyboardButton("✅ Done", callback_data="configure_goodbye_buttons")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"✅ Goodbye message buttons saved!\n\n"
                f"Added {len(buttons)} button(s).\n\n"
                f"What would you like to do next?",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("Try Again", callback_data="add_goodbye_buttons")],
                [InlineKeyboardButton("⬅️ Back", callback_data="configure_goodbye_buttons")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "⚠️ No valid buttons found. Please use the format:\n"
                "<code>Button Text - URL</code>\n\n"
                "Would you like to try again?",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return
        
        context.user_data['waiting_for_goodbye_buttons'] = False


async def handle_self_destruct_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle self-destruct time configuration input"""
    chat_id = update.effective_chat.id
    
    # Handle hours input
    if context.user_data.get('waiting_for_destruct_hours'):
        text = update.message.text
        
        if text == "/cancel":
            await update.message.reply_text("Cancelled.")
            context.user_data['waiting_for_destruct_hours'] = False
            return
        
        if text == "/skip":
            update_group_setting(chat_id, self_destruct_hours=0)
            await update.message.reply_text("Hours set to 0.")
            context.user_data['waiting_for_destruct_hours'] = False
            return
        
        try:
            hours = int(text)
            if 0 <= hours <= 23:
                update_group_setting(chat_id, self_destruct_hours=hours)
                await update.message.reply_text(f"✅ Hours set to {hours}.")
            else:
                await update.message.reply_text("❌ Please enter a value between 0 and 23.")
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please try again.")
            return
        
        context.user_data['waiting_for_destruct_hours'] = False
    
    # Handle minutes input
    elif context.user_data.get('waiting_for_destruct_minutes'):
        text = update.message.text
        
        if text == "/cancel":
            await update.message.reply_text("Cancelled.")
            context.user_data['waiting_for_destruct_minutes'] = False
            return
        
        if text == "/skip":
            update_group_setting(chat_id, self_destruct_minutes=0)
            await update.message.reply_text("Minutes set to 0.")
            context.user_data['waiting_for_destruct_minutes'] = False
            return
        
        try:
            minutes = int(text)
            if 0 <= minutes <= 59:
                update_group_setting(chat_id, self_destruct_minutes=minutes)
                await update.message.reply_text(f"✅ Minutes set to {minutes}.")
            else:
                await update.message.reply_text("❌ Please enter a value between 0 and 59.")
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please try again.")
            return
        
        context.user_data['waiting_for_destruct_minutes'] = False
    
    # Handle seconds input
    elif context.user_data.get('waiting_for_destruct_seconds'):
        text = update.message.text
        
        if text == "/cancel":
            await update.message.reply_text("Cancelled.")
            context.user_data['waiting_for_destruct_seconds'] = False
            return
        
        if text == "/skip":
            update_group_setting(chat_id, self_destruct_seconds=30)
            await update.message.reply_text("Seconds set to default 30.")
            context.user_data['waiting_for_destruct_seconds'] = False
            return
        
        try:
            seconds = int(text)
            if 5 <= seconds <= 59:
                update_group_setting(chat_id, self_destruct_seconds=seconds)
                await update.message.reply_text(f"✅ Seconds set to {seconds}.")
            else:
                await update.message.reply_text("❌ Please enter a value between 5 and 59 (minimum 5 seconds).")
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please try again.")
            return
        
        context.user_data['waiting_for_destruct_seconds'] = False
