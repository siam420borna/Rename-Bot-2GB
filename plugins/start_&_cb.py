from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from helper.database import jishubotz
from config import Config, Txt  

# -------------------- Button Layouts --------------------

START_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 ʜᴇʟᴘ", callback_data="help"),
     InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
    [InlineKeyboardButton("👤 ᴘʀᴏꜰɪʟᴇ", callback_data="profile"),
     InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")],
    [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://telegram.me/TechifyRahul")],
    [InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
])

HELP_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data="meta")],
    [InlineKeyboardButton("🔤 ᴘʀᴇꜰɪx", callback_data="prefix"),
     InlineKeyboardButton("🔚 ꜱᴜꜰꜰɪx", callback_data="suffix")],
    [InlineKeyboardButton("🖼️ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="thumbnail"),
     InlineKeyboardButton("📝 ᴄᴀᴘᴛɪᴏɴ", callback_data="caption")],
    [InlineKeyboardButton("🏠 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
])

ABOUT_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("📂 ɢɪᴛʜᴜʙ", url="https://github.com/TechifyBots"),
     InlineKeyboardButton("💸 ᴅᴏɴᴀᴛᴇ", callback_data="donate")],
    [InlineKeyboardButton("🏠 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
])

BACK_CLOSE = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"),
     InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
])

# -------------------- Start Command --------------------

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await jishubotz.add_user(client, message)                
    if Config.START_PIC:
        await message.reply_photo(
            Config.START_PIC,
            caption=Txt.START_TXT.format(user.mention),
            reply_markup=START_BUTTON
        )       
    else:
        await message.reply_text(
            text=Txt.START_TXT.format(user.mention),
            reply_markup=START_BUTTON,
            disable_web_page_preview=True
        )

# -------------------- Callback Query Handler --------------------

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 

    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=START_BUTTON
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTON
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=ABOUT_BUTTON
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ᴍᴏʀᴇ ʙᴏᴛs", url="https://telegram.me/TechifyBots/8")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="about"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "meta":
        await query.message.edit_caption(
            caption=Txt.SEND_METADATA,
            reply_markup=BACK_CLOSE
        )

    elif data == "prefix":
        await query.message.edit_caption(
            caption=Txt.PREFIX,
            reply_markup=BACK_CLOSE
        )

    elif data == "suffix":
        await query.message.edit_caption(
            caption=Txt.SUFFIX,
            reply_markup=BACK_CLOSE
        )

    elif data == "caption":
        await query.message.edit_caption(
            caption=Txt.CAPTION_TXT,
            reply_markup=BACK_CLOSE
        )

    elif data == "thumbnail":
        await query.message.edit_caption(
            caption=Txt.THUMBNAIL_TXT,
            reply_markup=BACK_CLOSE
        )

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()

    elif data == "profile":
        user = query.from_user
        text = f"""
**Your Profile**
━━━━━━━━━━━━━━━━━
**Name:** {user.first_name}
**Username:** @{user.username if user.username else 'N/A'}
**User ID:** `{user.id}`
**Premium User:** {"Yes" if user.is_premium else "No"}
━━━━━━━━━━━━━━━━━
        """
        await query.message.edit(
            text=text,
            reply_markup=BACK_CLOSE
        )

    elif data == "settings":
        await query.message.edit(
            text="""
**Settings Panel**
━━━━━━━━━━━━━━━━━
Here you will be able to configure:
• Custom Thumbnail
• Caption Templates
• Prefix/Suffix
• Auto Rename Mode

(This section is under development!)
━━━━━━━━━━━━━━━━━
            """,
            reply_markup=BACK_CLOSE
        )

    elif data.startswith("sendAlert"):
        user_id = int(data.split("_")[1].strip())
        reason = str(data.split("_")[2])
        try:
            await client.send_message(user_id , f"<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ʙʏ [ʀᴀʜᴜʟ](https://telegram.me/callownerbot)\nʀᴇᴀsᴏɴ : {reason}</b>")
            await query.message.edit(f"<b>Aʟᴇʀᴛ sᴇɴᴛ ᴛᴏ <code>{user_id}</code>\nʀᴇᴀsᴏɴ : {reason}</b>")
        except Exception as e:
            await query.message.edit(f"<b>sʀʏ ɪ ɢᴏᴛ ᴛʜɪs ᴇʀʀᴏʀ : {e}</b>")

    elif data.startswith('noAlert'):
        user_id = int(data.split("_")[1].strip())
        await query.message.edit(f"<b>Tʜᴇ ʙᴀɴ ᴏɴ <code>{user_id}</code> ᴡᴀs ᴇxᴇᴄᴜᴛᴇᴅ sɪʟᴇɴᴛʟʏ.</b>")

    elif data.startswith('sendUnbanAlert'):
        user_id = int(data.split("_")[1].strip())
        try:
            unban_text = "<b>ʜᴜʀʀᴀʏ..ʏᴏᴜ ᴀʀᴇ ᴜɴʙᴀɴɴᴇᴅ ʙʏ [ʀᴀʜᴜʟ](https://telegram.me/callownerbot)</b>"
            await client.send_message(user_id , unban_text)
            await query.message.edit(f"<b>Uɴʙᴀɴɴᴇᴅ Aʟᴇʀᴛ sᴇɴᴛ ᴛᴏ <code>{user_id}</code>\nᴀʟᴇʀᴛ ᴛᴇxᴛ : {unban_text}</b>")
        except Exception as e:
            await query.message.edit(f"<b>sʀʏ ɪ ɢᴏᴛ ᴛʜɪs ᴇʀʀᴏʀ : {e}</b>")

    elif data.startswith('NoUnbanAlert'):
        user_id = int(data.split("_")[1].strip())
        await query.message.edit(f"Tʜᴇ ᴜɴʙᴀɴ ᴏɴ <code>{user_id}</code> ᴡᴀs ᴇxᴇᴄᴜᴛᴇᴅ sɪʟᴇɴᴛʟʏ.")



#oooooooother commend



from pyrogram import Client, filters
from helper.database import jishubotz

@Client.on_message(filters.private & filters.command("set_thumb_size"))
async def set_thumb_size(client, message):
    try:
        args = message.text.split(" ", 1)
        if len(args) != 2:
            return await message.reply_text("❗ Usage:\n`/set_thumb_size widthxheight`\nExample: `/set_thumb_size 640x360`", quote=True)

        width, height = map(int, args[1].lower().split("x"))
        if width < 100 or height < 100:
            return await message.reply_text("❌ Size too small. Use something like `640x360` or higher.", quote=True)

        await jishubotz.set_thumb_size(message.from_user.id, f"{width}x{height}")
        await message.reply_text(f"✅ Thumbnail size set to `{width}x{height}`", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Failed to set size.\nError: `{e}`", quote=True)