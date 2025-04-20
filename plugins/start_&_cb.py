from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from helper.database import jishubotz, set_watermark, get_watermark, del_watermark
from config import Config


class Txt:
    START_TXT = """
**👋 Hey {0}**,  
𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 **𝐒𝐢𝐚𝐦'𝐬 𝐑𝐞𝐧𝐚𝐦𝐞𝐫 𝐁𝐨𝐭**!

With this bot, you can:
• 𝗥𝗲𝗻𝗮𝗺𝗲 & 𝗲𝗱𝗶𝘁 𝗳𝗶𝗹𝗲𝘀  
• 𝗖𝗼𝗻𝘃𝗲𝗿𝘁 𝘃𝗶𝗱𝗲𝗼 𝘁𝗼 𝗳𝗶𝗹𝗲 & 𝘃𝗶𝗰𝗲 𝘃𝗲𝗿𝘀𝗮  
• 𝗦𝗲𝘁 𝗰𝘂𝘀𝘁𝗼𝗺: thumbnail, caption, prefix & suffix  

**⚠️ Note:**  
_Adult content renaming is strictly prohibited. Violators will be banned permanently!_
"""

    HELP_TXT = """
**🛠 How to Use This Bot?**

1. **Send any file** you want to rename  
2. Bot will ask for new name — reply with it  
3. You’ll get the renamed file with metadata

**⚙ Features:**  
• `/set_caption` - Set custom caption  
• `/set_thumbnail` - Set custom thumbnail  
• `/set_prefix` or `/set_suffix` - Customize filename  
• `/set_watermark` - Add watermark text to video thumbnails  
• `/del_watermark` - Remove watermark

Use the buttons below for more info.
"""

    ABOUT_TXT = """
**🤖 Bot Info:**

• **Name:** Siam’s Renamer Bot  
• **Language:** Python3  
• **Library:** Pyrogram  
• **Hosted On:** Railway  
• **Creator:** [Siam (TechifyRahul)](https://t.me/TechifyRahul)

This bot is completely free and open source.
"""

    DONATE_TXT = """
**💸 Support the Developer**

If you find this bot useful, consider supporting development:

• UPI: `siam@ybl`  
• PayPal: _Coming Soon_

Even a small amount is appreciated!  
"""

    SEND_METADATA = "**📝 Please send your custom metadata (Title, Artist, etc).**"
    PREFIX = "**✍ Send a prefix to add before filename.**"
    SUFFIX = "**✍ Send a suffix to add after filename.**"
    CAPTION_TXT = "**🖋 Send a custom caption (use {filename} to include file name).**"
    THUMBNAIL_TXT = "**🖼 Send an image to set as custom thumbnail.**"


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await jishubotz.add_user(client, message)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 ᴀʙᴏᴜᴛ", callback_data="about"),
         InlineKeyboardButton("🛠 ʜᴇʟᴘ", callback_data="help")],
        [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/TechifyRahul")]
    ])

    try:
        if Config.START_PIC:
            await message.reply_photo(
                photo=Config.START_PIC,
                caption=Txt.START_TXT.format(user.mention),
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                text=Txt.START_TXT.format(user.mention),
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
    except Exception as e:
        await message.reply_text(f"⚠️ Error in /start:\n`{e}`")


@Client.on_callback_query()
async def callback(client, query: CallbackQuery):
    data = query.data
    user = query.from_user

    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 ᴀʙᴏᴜᴛ", callback_data="about"),
                 InlineKeyboardButton("🛠 ʜᴇʟᴘ", callback_data="help")],
                [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/TechifyRahul")]
            ])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data="meta")],
                [InlineKeyboardButton("📌 ᴘʀᴇꜰɪx", callback_data="prefix"),
                 InlineKeyboardButton("📍 sᴜꜰꜰɪx", callback_data="suffix")],
                [InlineKeyboardButton("🖋 ᴄᴀᴘᴛɪᴏɴ", callback_data="caption"),
                 InlineKeyboardButton("🖼 ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="thumbnail")],
                [InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="start")]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 ʀᴇᴘᴏ", url="https://github.com/TechifyBots"),
                 InlineKeyboardButton("💸 ᴅᴏɴᴀᴛᴇ", callback_data="donate")],
                [InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="start")]
            ])
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ᴍᴏʀᴇ ʙᴏᴛꜱ", url="https://t.me/TechifyBots/8")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="about"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "meta":
        await query.message.edit_text(
            text=Txt.SEND_METADATA,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "prefix":
        await query.message.edit_text(
            text=Txt.PREFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "suffix":
        await query.message.edit_text(
            text=Txt.SUFFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "thumbnail":
        await query.message.edit_text(
            text=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass


@Client.on_message(filters.private & filters.command("set_watermark"))
async def save_watermark(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/set_watermark YourTextHere`")
    text = message.text.split(None, 1)[1]
    await set_watermark(message.from_user.id, text)
    await message.reply_text(f"✅ Watermark set to: `{text}`")


@Client.on_message(filters.private & filters.command("del_watermark"))
async def remove_watermark(client, message: Message):
    await del_watermark(message.from_user.id)
    await message.reply_text("🗑️ Watermark removed.")