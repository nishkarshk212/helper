"""
User management features: ban, warn, mute, promote with custom roles and permissions
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from database import get_or_create_group, update_group_setting
from font import to_monospace_uppercase
import json

OWNER_ID = 8791884726  # Group creator ID


# ---------------- ADMIN CHECK ---------------- #

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]


async def is_owner(update: Update):
    return update.effective_user.id == OWNER_ID


# ---------------- GET TARGET USER ---------------- #

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat.id
    
    # Method 1: Reply to message (most reliable)
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    
    # Method 2 & 3: Command argument (username or user ID)
    if context.args:
        arg = context.args[0]
        
        # If numeric, treat as user ID
        if arg.isdigit():
            return int(arg)
        
        # If username, try to lookup
        username = arg.replace("@", "").lower()
        
        # Try to find user by iterating through chat administrators first
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            for admin in admins:
                if admin.user.username and admin.user.username.lower() == username:
                    return admin.user.id
        except:
            pass
        
        # Try with @ prefix (works in some API versions)
        try:
            member = await context.bot.get_chat_member(chat_id, f"@{username}")
            return member.user.id
        except:
            pass
    
    return None


async def handle_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user from the group"""
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only command")
    
    user_id = await get_target_user(update, context)
    
    if not user_id:
        return await update.message.reply_text(
            "Usage:\n"
            "/ban @username\n"
            "/ban user_id\n"
            "or reply to user"
        )
    
    try:
        await context.bot.ban_chat_member(
            update.effective_chat.id,
            user_id
        )
        await update.message.reply_text("🚫 User banned")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def handle_warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warn a user"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user is admin
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    
    if chat_member.status not in ['creator', 'administrator']:
        await update.message.reply_text("Only admins can warn users.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Reply to a user's message and use /warn to warn them."
        )
        return
    
    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    settings = get_or_create_group(chat_id)
    
    # Get current warns
    try:
        warns = json.loads(settings.user_warns)
    except:
        warns = {}
    
    user_id_str = str(target_user.id)
    current_warns = warns.get(user_id_str, 0) + 1
    warns[user_id_str] = current_warns
    
    update_group_setting(chat_id, user_warns=json.dumps(warns))
    
    await update.message.reply_text(
        f"⚠️ {target_user.mention_html()} has been warned!\n"
        f"Warning {current_warns}/3",
        parse_mode='HTML'
    )
    
    # Auto-ban after 3 warnings
    if current_warns >= 3:
        try:
            await context.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=target_user.id
            )
            await update.message.reply_text(
                f"🚫 {target_user.mention_html()} has been auto-banned after 3 warnings!",
                parse_mode='HTML'
            )
            warns[user_id_str] = 0  # Reset warns
            update_group_setting(chat_id, user_warns=json.dumps(warns))
        except Exception as e:
            await update.message.reply_text(f"Error auto-banning: {e}")


async def handle_mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute a user (restrict from sending messages)"""
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only command")
    
    user_id = await get_target_user(update, context)
    
    if not user_id:
        return await update.message.reply_text(
            "Usage:\n"
            "/mute @username\n"
            "/mute user_id\n"
            "or reply to user"
        )
    
    try:
        permissions = ChatPermissions(can_send_messages=False)
        
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            permissions=permissions
        )
        await update.message.reply_text("🔇 User muted")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def handle_unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unmute a user"""
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only command")
    
    user_id = await get_target_user(update, context)
    
    if not user_id:
        return await update.message.reply_text(
            "Usage:\n"
            "/unmute @username\n"
            "/unmute user_id\n"
            "or reply to user"
        )
    
    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            permissions=permissions
        )
        await update.message.reply_text("🔊 User unmuted")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def handle_promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote user with custom role and permission selection using toggle buttons"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user is creator (only creator can use custom permissions)
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    
    if chat_member.status != 'creator':
        await update.message.reply_text("Only the group creator can promote users with custom permissions.")
        return
    
    # Get target user using admin.py logic
    user_id = await get_target_user(update, context)
    
    if not user_id:
        await update.message.reply_text(
            "Reply to a user's message, mention them (@username), or provide their user ID,\n"
            "then use /promote to configure their permissions.\n\n"
            "<b>Examples:</b>\n"
            "• Reply to message + /promote\n"
            "• /promote @username\n"
            "• /promote 123456789",
            parse_mode='HTML'
        )
        return
    
    # Initialize default permissions (all disabled)
    context.user_data[f'promote_{user_id}'] = {
        'role': 'custom',
        'permissions': {
            'can_change_info': False,
            'can_delete_messages': False,
            'can_restrict_members': False,
            'can_invite_users': False,
            'can_pin_messages': False,
            'can_manage_video_chats': False,
            'is_anonymous': False,
            'can_promote_members': False,
            'can_mute_users': False
        }
    }
    
    # Show permission configuration with toggle buttons
    await show_permission_keyboard(query=None, update=update, context=context, target_user_id=user_id)


async def show_permission_keyboard(query, update, context, target_user_id):
    """Show permission configuration keyboard"""
    promote_data = context.user_data.get(f'promote_{target_user_id}', {})
    perms = promote_data.get('permissions', {})
    
    # Use short codes for permissions to stay within 64-byte callback_data limit
    perm_codes = {
        'can_change_info': 'ci',
        'can_delete_messages': 'dm',
        'can_restrict_members': 'rm',
        'can_invite_users': 'iu',
        'can_pin_messages': 'pm',
        'can_manage_video_chats': 'vc',
        'is_anonymous': 'an',
        'can_promote_members': 'ap'
    }
    
    keyboard = [
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_change_info', False) else '❌'} Change Group Info",
            callback_data=f"pt_ci_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_delete_messages', False) else '❌'} Delete Messages",
            callback_data=f"pt_dm_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_restrict_members', False) else '❌'} Ban Users",
            callback_data=f"pt_rm_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_invite_users', False) else '❌'} Invite Users via Link",
            callback_data=f"pt_iu_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_pin_messages', False) else '❌'} Pin Messages",
            callback_data=f"pt_pm_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_manage_video_chats', False) else '❌'} Manage Video Chats",
            callback_data=f"pt_vc_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('is_anonymous', False) else '❌'} Remain Anonymous",
            callback_data=f"pt_an_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_promote_members', False) else '❌'} Add New Admins",
            callback_data=f"pt_ap_{target_user_id}"
        )],
        [InlineKeyboardButton(
            f"{'✅' if perms.get('can_mute_users', False) else '❌'} Mute Users",
            callback_data=f"pt_mu_{target_user_id}"
        )],
        [InlineKeyboardButton("✅ Promote User", callback_data=f"cp_{target_user_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_promote")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "<b>Configure Admin Permissions:</b>\n\n"
        "Click on permissions to toggle them (✅/❌)\n"
        "Then click 'Promote User' to apply."
    )
    
    if query:
        await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='HTML')


async def handle_permission_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle individual permissions"""
    query = update.callback_query
    
    action = query.data
    parts = action.split("_")
    # Format: pt_ci_123456789
    perm_code = parts[1]  # ci, dm, rm, etc.
    target_user_id = int(parts[2])
    
    print(f"DEBUG: Permission toggle clicked - action: {action}, perm_code: {perm_code}, user_id: {target_user_id}")
    
    await query.answer()
    
    # Map short codes back to full permission names
    code_to_perm = {
        'ci': 'can_change_info',
        'dm': 'can_delete_messages',
        'rm': 'can_restrict_members',
        'iu': 'can_invite_users',
        'pm': 'can_pin_messages',
        'vc': 'can_manage_video_chats',
        'an': 'is_anonymous',
        'ap': 'can_promote_members',
        'mu': 'can_mute_users'
    }
    
    perm_name = code_to_perm.get(perm_code)
    if not perm_name:
        print(f"DEBUG: Invalid permission code: {perm_code}")
        await query.answer("Invalid permission", show_alert=True)
        return
    
    # Get current permissions
    promote_data = context.user_data.get(f'promote_{target_user_id}', {})
    if 'permissions' not in promote_data:
        promote_data['permissions'] = {}
    
    # Toggle the permission
    current_value = promote_data['permissions'].get(perm_name, False)
    promote_data['permissions'][perm_name] = not current_value
    context.user_data[f'promote_{target_user_id}'] = promote_data
    
    print(f"DEBUG: Toggled {perm_name} from {current_value} to {not current_value}")
    
    # Refresh the keyboard
    await show_permission_keyboard(query=query, update=None, context=context, target_user_id=target_user_id)


async def handle_confirm_promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute promotion with selected permissions"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    parts = action.split("_")
    # Format: cp_123456789
    target_user_id = int(parts[1])
    
    chat_id = query.message.chat_id
    
    promote_data = context.user_data.get(f'promote_{target_user_id}', {})
    perms = promote_data.get('permissions', {})
    role = promote_data.get('role', 'custom')
    
    try:
        # Promote user with specific permissions
        await context.bot.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user_id,
            can_change_info=perms.get('can_change_info', False),
            can_delete_messages=perms.get('can_delete_messages', False),
            can_invite_users=perms.get('can_invite_users', False),
            can_restrict_members=perms.get('can_restrict_members', False),
            can_pin_messages=perms.get('can_pin_messages', False),
            can_promote_members=perms.get('can_promote_members', False),
            is_anonymous=perms.get('is_anonymous', False),
            can_manage_video_chats=perms.get('can_manage_video_chats', False)
        )
        
        # Save custom role with full permissions
        settings = get_or_create_group(chat_id)
        try:
            custom_roles = json.loads(settings.custom_admin_roles)
        except:
            custom_roles = {}
        
        # Get user info for better display
        try:
            member = await context.bot.get_chat_member(chat_id, target_user_id)
            user_name = member.user.full_name
            username = f"@{member.user.username}" if member.user.username else "No username"
        except:
            user_name = f"User {target_user_id}"
            username = "Unknown"
        
        custom_roles[str(target_user_id)] = {
            'role': role,
            'tag': f"@{role.capitalize()}",
            'name': user_name,
            'username': username,
            'permissions': {
                'can_change_info': perms.get('can_change_info', False),
                'can_delete_messages': perms.get('can_delete_messages', False),
                'can_restrict_members': perms.get('can_restrict_members', False),
                'can_invite_users': perms.get('can_invite_users', False),
                'can_pin_messages': perms.get('can_pin_messages', False),
                'can_manage_video_chats': perms.get('can_manage_video_chats', False),
                'is_anonymous': perms.get('is_anonymous', False),
                'can_promote_members': perms.get('can_promote_members', False),
                'can_mute_users': perms.get('can_mute_users', False)
            },
            'promoted_at': str(__import__('datetime').datetime.now().isoformat())
        }
        update_group_setting(chat_id, custom_admin_roles=json.dumps(custom_roles))
        
        role_names = {
            'admin': 'Administrator',
            'moderator': 'Moderator',
            'muter': 'Muter',
            'custom': 'Custom Admin'
        }
        
        await query.edit_message_text(
            f"✅ User has been promoted to {role_names.get(role, 'Admin')}!\n\n"
            f"<b>Permissions:</b>\n"
            f"• Change Info: {'Yes' if perms.get('can_change_info', False) else 'No'}\n"
            f"• Delete Messages: {'Yes' if perms.get('can_delete_messages', False) else 'No'}\n"
            f"• Ban Users: {'Yes' if perms.get('can_restrict_members', False) else 'No'}\n"
            f"• Invite Users: {'Yes' if perms.get('can_invite_users', False) else 'No'}\n"
            f"• Pin Messages: {'Yes' if perms.get('can_pin_messages', False) else 'No'}\n"
            f"• Manage Video Chats: {'Yes' if perms.get('can_manage_video_chats', False) else 'No'}\n"
            f"• Anonymous: {'Yes' if perms.get('is_anonymous', False) else 'No'}\n"
            f"• Add New Admins: {'Yes' if perms.get('can_promote_members', False) else 'No'}\n"
            f"• Mute Users: {'Yes' if perms.get('can_mute_users', False) else 'No'}",
            parse_mode='HTML'
        )
        
        # Clean up temp data
        context.user_data.pop(f'promote_{target_user_id}', None)
        
    except Exception as e:
        await query.edit_message_text(f"Error promoting user: {e}")


async def handle_demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demote a user (remove admin privileges)"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user is creator
    chat_member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    
    if chat_member.status != 'creator':
        await update.message.reply_text("Only the group creator can demote admins.")
        return
    
    # Get target user using admin.py logic
    user_id = await get_target_user(update, context)
    
    if not user_id:
        await update.message.reply_text(
            "Usage:\n"
            "/demote @username\n"
            "/demote user_id\n"
            "or reply to user"
        )
        return
    
    try:
        # Demote user by promoting without any permissions
        await context.bot.promote_chat_member(
            update.effective_chat.id,
            user_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            is_anonymous=False,
            can_manage_video_chats=False
        )
        
        # Remove from custom roles
        settings = get_or_create_group(update.effective_chat.id)
        try:
            custom_roles = json.loads(settings.custom_admin_roles)
        except:
            custom_roles = {}
        
        user_id_str = str(user_id)
        if user_id_str in custom_roles:
            removed_role = custom_roles[user_id_str].get('role', 'admin')
            del custom_roles[user_id_str]
            update_group_setting(update.effective_chat.id, custom_admin_roles=json.dumps(custom_roles))
            print(f"Removed {user_id} from custom roles (was {removed_role})")
        
        await update.message.reply_text("✅ User demoted")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ---------------- USER ID ---------------- #

async def handle_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user ID"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user provided an argument (username or ID)
    has_arg = bool(context.args)
    
    # Get target user
    user_id = await get_target_user(update, context)
    
    if not user_id:
        # If no target and no args, return chat ID and current user ID
        if not has_arg:
            chat_id = update.effective_chat.id
            current_user_id = update.effective_user.id
            
            message = (
                f"<b>Chat ID:</b> <code>{chat_id}</code>\n"
                f"<b>Your ID:</b> <code>{current_user_id}</code>\n\n"
                f"To get another user's ID:\n"
                f"• Reply to their message + /id\n"
                f"• /id @username\n"
                f"• /id user_id"
            )
            return await update.message.reply_text(message, parse_mode='HTML')
        else:
            # User provided arg but lookup failed
            return await update.message.reply_text(
                "❌ User not found!\n\n"
                "⚠️ Username lookup has limitations:\n"
                "• Only works for group administrators\n"
                "• User must have a username set\n"
                "• Username must be spelled correctly\n\n"
                "✅ Recommended: Reply to their message with /id\n"
                "💡 Or use their numeric user ID: /id 123456789"
            )
    
    # Return target user ID
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        user = member.user
        
        message = (
            f"<b>User ID:</b> <code>{user.id}</code>\n"
            f"<b>Name:</b> {user.full_name}\n"
        )
        
        if user.username:
            message += f"<b>Username:</b> @{user.username}\n"
        
        message += f"\nTo use this ID in commands, copy the number above."
        
        return await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        return await update.message.reply_text(f"❌ Error: {e}")


# ---------------- USER INFO ---------------- #

async def handle_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get detailed user information"""
    if not update.effective_chat or not update.message:
        return
    
    # Check if user provided an argument
    has_arg = bool(context.args)
    
    # Get target user
    user_id = await get_target_user(update, context)
    
    if not user_id:
        # If no target and no args, show info for current user
        if not has_arg:
            user_id = update.effective_user.id
        else:
            # User provided arg but lookup failed
            return await update.message.reply_text(
                "❌ User not found!\n\n"
                "⚠️ Username lookup has limitations:\n"
                "• Only works for group administrators\n"
                "• User must have a username set\n"
                "• Username must be spelled correctly\n\n"
                "✅ Recommended: Reply to their message with /info\n"
                "💡 Or use their numeric user ID: /info 123456789"
            )
    
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        user = member.user
        
        # Build info message
        info = f"<b>👤 User Information</b>\n\n"
        info += f"<b>ID:</b> <code>{user.id}</code>\n"
        info += f"<b>Name:</b> {user.full_name}\n"
        
        if user.username:
            info += f"<b>Username:</b> @{user.username}\n"
        
        if user.language_code:
            info += f"<b>Language:</b> {user.language_code.upper()}\n"
        
        info += f"<b>Is Bot:</b> {'Yes' if user.is_bot else 'No'}\n"
        info += f"<b>Status:</b> {member.status.capitalize()}\n"
        
        # Add admin title if exists (only for administrators)
        if hasattr(member, 'custom_title') and member.custom_title:
            info += f"<b>Admin Title:</b> {member.custom_title}\n"
        
        info += f"\n<b>Chat ID:</b> <code>{update.effective_chat.id}</code>"
        
        return await update.message.reply_text(info, parse_mode='HTML')
    except Exception as e:
        return await update.message.reply_text(f"❌ Error getting user info: {e}")


# ---------------- LIST CUSTOM ADMINS ---------------- #

async def handle_admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all custom admins with their permissions"""
    if not update.effective_chat or not update.message:
        return
    
    settings = get_or_create_group(update.effective_chat.id)
    
    try:
        custom_roles = json.loads(settings.custom_admin_roles)
    except:
        custom_roles = {}
    
    if not custom_roles:
        return await update.message.reply_text("No custom admins configured in this group.")
    
    # Build admin list message
    message = "<b>👥 Custom Administrators</b>\n\n"
    
    for user_id_str, role_data in custom_roles.items():
        role = role_data.get('role', 'custom')
        name = role_data.get('name', f'User {user_id_str}')
        username = role_data.get('username', 'No username')
        perms = role_data.get('permissions', {})
        promoted_at = role_data.get('promoted_at', 'Unknown')
        
        # Format role name
        role_names = {
            'admin': 'Administrator',
            'moderator': 'Moderator',
            'muter': 'Muter',
            'custom': 'Custom Admin'
        }
        role_name = role_names.get(role, 'Custom Admin')
        
        message += f"<b>{name}</b> {username}\n"
        message += f"└ Role: {role_name}\n"
        
        # Show key permissions
        enabled_perms = []
        if perms.get('can_delete_messages'):
            enabled_perms.append('Delete')
        if perms.get('can_restrict_members'):
            enabled_perms.append('Ban')
        if perms.get('can_invite_users'):
            enabled_perms.append('Invite')
        if perms.get('can_pin_messages'):
            enabled_perms.append('Pin')
        if perms.get('can_mute_users'):
            enabled_perms.append('Mute')
        if perms.get('can_promote_members'):
            enabled_perms.append('Add Admins')
        
        if enabled_perms:
            message += f"└ Permissions: {', '.join(enabled_perms)}\n"
        else:
            message += f"└ Permissions: Minimal\n"
        
        message += "\n"
    
    message += f"<i>Total: {len(custom_roles)} custom admin(s)</i>"
    
    await update.message.reply_text(message, parse_mode='HTML')
