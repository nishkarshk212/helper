from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

OWNER_ID = 8791884726  # change this

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

    # reply
    if message.reply_to_message:
        return message.reply_to_message.from_user.id

    # argument
    if context.args:
        arg = context.args[0]

        if arg.isdigit():
            return int(arg)

        username = arg.replace("@", "")

        try:
            member = await context.bot.get_chat_member(chat_id, username)
            return member.user.id
        except:
            return None

    return None


# ---------------- PROMOTE ---------------- #

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only command")

    user_id = await get_target_user(update, context)

    if not user_id:
        return await update.message.reply_text(
            "Usage:\n"
            "/promote @username\n"
            "/promote user_id\n"
            "or reply to user"
        )

    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id,
            user_id,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True
        )

        await update.message.reply_text("✅ User promoted")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ---------------- DEMOTE ---------------- #

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only command")

    user_id = await get_target_user(update, context)

    if not user_id:
        return await update.message.reply_text("Reply or give username")

    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id,
            user_id,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False
        )

        await update.message.reply_text("✅ User demoted")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ---------------- BAN ---------------- #

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only")

    user_id = await get_target_user(update, context)

    if not user_id:
        return await update.message.reply_text("Reply or give username")

    try:
        await context.bot.ban_chat_member(
            update.effective_chat.id,
            user_id
        )

        await update.message.reply_text("🚫 User banned")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ---------------- UNBAN ---------------- #

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only")

    user_id = await get_target_user(update, context)

    if not user_id:
        return await update.message.reply_text("Reply or give user id")

    try:
        await context.bot.unban_chat_member(
            update.effective_chat.id,
            user_id
        )

        await update.message.reply_text("✅ User unbanned")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ---------------- MUTE ---------------- #

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only")

    user_id = await get_target_user(update, context)

    if not user_id:
        return await update.message.reply_text("Reply or give username")

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


# ---------------- UNMUTE ---------------- #

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Admin only")

    user_id = await get_target_user(update, context)

    if not user_id:
        return await update.message.reply_text("Reply or give username")

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