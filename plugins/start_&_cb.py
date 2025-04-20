from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from helper.database import jishubotz, set_watermark, get_watermark, del_watermark
from config import Config


class Txt:
    START_TXT = """
**👋 হ্যালো {0}**,  
Welcome to **𝐒𝐢𝐚𝐦'𝐬 𝐑𝐞𝐧𝐚𝐦𝐞𝐫 𝐁𝐨𝐭**!

With this bot, you can:
• Rename & edit files  
• Convert video to file & vice versa  
• Set custom: thumbnail, caption, prefix & suffix  

**⚠️ Warning:**  
Adult content is strictly prohibited. Offenders will be **banned permanently**!
"""

    HELP_TXT = """
**🛠 How to Use This Bot?**

1. Just **send any file** you want to rename  
2. Bot will ask for new name — reply with it  
3. You’ll get the renamed file with metadata

**⚙ Features:**  
• `/set_caption` - Set custom caption  
• `/set_thumbnail` - Set custom thumbnail  
• `/set_prefix` or `/set_suffix` - Customize filename  
• `/set_watermark` - Add watermark text on video thumbnail  
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

    SEND_METADATA = "**📝 Send your custom metadata (Title, Artist, etc).**"
    PREFIX = "**✍ Send a prefix to add before filename.**"
    SUFFIX = "**✍ Send a suffix to add after filename.**"
    CAPTION_TXT = "**🖋 Send a custom caption (use {filename} to include file name).**"
    THUMBNAIL_TXT = "**🖼 Send an image to set as custom thumbnail.**"


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await jishubotz.add_user(client, message)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 About", callback_data="about"),
         InlineKeyboardButton("🛠 Help", callback_data="help")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/TechifyRahul")]
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
                [InlineKeyboardButton("📚 About", callback_data="about"),
                 InlineKeyboardButton("🛠 Help", callback_data="help")],
                [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/TechifyRahul")]
            ])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Metadata", callback_data="meta")],
                [InlineKeyboardButton("📌 Prefix", callback_data="prefix"),
                 InlineKeyboardButton("📍 Suffix", callback_data="suffix")],
                [InlineKeyboardButton("🖋 Caption", callback_data="caption"),
                 InlineKeyboardButton("🖼 Thumbnail", callback_data="thumbnail")],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Repo", url="https://github.com/TechifyBots"),
                 InlineKeyboardButton("💸 Donate", callback_data="donate")],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ])
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 More Bots", url="https://t.me/TechifyBots/8")],
                [InlineKeyboardButton("🔙 Back", callback_data="about"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "meta":
        await query.message.edit_text(
            text=Txt.SEND_METADATA,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "prefix":
        await query.message.edit_text(
            text=Txt.PREFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "suffix":
        await query.message.edit_text(
            text=Txt.SUFFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "thumbnail":
        await query.message.edit_text(
            text=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
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