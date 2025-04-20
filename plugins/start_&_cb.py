from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from helper.database import jishubotz
from config import Config, Txt

# ──────── Button Layouts ────────

START_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Help", callback_data="help"),
     InlineKeyboardButton("ℹ️ About", callback_data="about")],
    [InlineKeyboardButton("👤 Profile", callback_data="profile"),
     InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    [InlineKeyboardButton("👨‍💻 Developer", url="https://telegram.me/TechifyRahul")],
    [InlineKeyboardButton("❌ Close", callback_data="close")]
])

HELP_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 Metadata", callback_data="meta")],
    [InlineKeyboardButton("🔤 Prefix", callback_data="prefix"),
     InlineKeyboardButton("🔚 Suffix", callback_data="suffix")],
    [InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumbnail"),
     InlineKeyboardButton("📝 Caption", callback_data="caption")],
    [InlineKeyboardButton("🏠 Home", callback_data="start")]
])

ABOUT_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("📂 GitHub", url="https://github.com/TechifyBots"),
     InlineKeyboardButton("💸 Donate", callback_data="donate")],
    [InlineKeyboardButton("🏠 Home", callback_data="start")]
])

BACK_CLOSE = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 Back", callback_data="help"),
     InlineKeyboardButton("❌ Close", callback_data="close")]
])

# ──────── /start Command ────────

@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    await jishubotz.add_user(client, message)

    await message.chat.do("upload_photo")  # animation typing effect
    await message.reply_photo(
        photo=Config.START_PIC,  # Add your image URL or file ID in config.py
        caption=Txt.START_TXT.format(user.mention),
        reply_markup=START_BUTTON
    )

# ──────── Callback Handler ────────

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user = query.from_user

    await query.message.chat.do("typing")

    if data == "start":
        try:
            await query.message.delete()
        except:
            pass
        await query.message.chat.send_photo(
            photo=Config.START_PIC,
            caption=Txt.START_TXT.format(user.mention),
            reply_markup=START_BUTTON
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            reply_markup=HELP_BUTTON,
            disable_web_page_preview=True
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            reply_markup=ABOUT_BUTTON,
            disable_web_page_preview=True
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 More Bots", url="https://telegram.me/TechifyBots/8")],
                [InlineKeyboardButton("🔙 Back", callback_data="about"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ]),
            disable_web_page_preview=True
        )

    elif data == "profile":
        text = f"""**Your Profile**

━━━━━━━━━━━━━━━━━
Name: {user.first_name}
Username: @{user.username or 'N/A'}
User ID: {user.id}
Premium User: {"Yes" if user.is_premium else "No"}
━━━━━━━━━━━━━━━━━"""
        await query.message.edit_text(text, reply_markup=BACK_CLOSE)

    elif data == "settings":
        await query.message.edit_text(
            text="""
**Settings Panel**
━━━━━━━━━━━━━━━━━
Customize your experience:
• Custom Thumbnail
• Caption Templates
• Prefix / Suffix
• Auto Rename Mode (coming soon!)
━━━━━━━━━━━━━━━━━
""",
            reply_markup=BACK_CLOSE
        )

    elif data == "meta":
        await query.message.edit_text(text=Txt.SEND_METADATA, reply_markup=BACK_CLOSE)

    elif data == "prefix":
        await query.message.edit_text(text=Txt.PREFIX, reply_markup=BACK_CLOSE)

    elif data == "suffix":
        await query.message.edit_text(text=Txt.SUFFIX, reply_markup=BACK_CLOSE)

    elif data == "caption":
        await query.message.edit_text(text=Txt.CAPTION_TXT, reply_markup=BACK_CLOSE)

    elif data == "thumbnail":
        await query.message.edit_text(text=Txt.THUMBNAIL_TXT, reply_markup=BACK_CLOSE)

    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass

    # ───── Admin Controls ─────
    elif data.startswith("sendAlert"):
        user_id, reason = int(data.split("_")[1]), data.split("_")[2]
        try:
            await client.send_message(user_id, f"You're banned.\nReason: {reason}")
            await query.message.edit_text(f"Alert sent to `{user_id}`.\nReason: {reason}")
        except Exception as e:
            await query.message.edit_text(f"Failed to send alert.\nError: {e}")

    elif data.startswith("noAlert"):
        user_id = int(data.split("_")[1])
        await query.message.edit_text(f"Ban on `{user_id}` executed silently.")

    elif data.startswith("sendUnbanAlert"):
        user_id = int(data.split("_")[1])
        try:
            await client.send_message(user_id, "You have been unbanned.")
            await query.message.edit_text(f"Unban alert sent to `{user_id}`.")
        except Exception as e:
            await query.message.edit_text(f"Failed to send unban alert.\nError: {e}")

    elif data.startswith("NoUnbanAlert"):
        user_id = int(data.split("_")[1])
        await query.message.edit_text(f"Unban on `{user_id}` executed silently.")