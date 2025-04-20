from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from helper.database import jishubotz, set_watermark, del_watermark
from config import Config


class Txt:
    START_TXT = """
**Hello {0}**,  
Welcome to **Siam's Renamer Bot**!

With this bot, you can:
• Rename any file  
• Convert video to file  
• Set custom thumbnail, caption, prefix & suffix  

**⚠️ Warning:**  
Pornographic or adult content will result in permanent ban!
"""

    HELP_TXT = """
**How to Use:**

1. Send any file  
2. Bot will ask for new name  
3. Get your renamed file instantly  

**Features:**  
• `/set_caption` - Set custom caption  
• `/set_thumbnail` - Set thumbnail  
• `/set_prefix` or `/set_suffix` - Customize filename  
• `/set_watermark` - Set video watermark  
• `/del_watermark` - Remove watermark  
"""

    ABOUT_TXT = """
**Bot Info:**

• Name: Siam’s Renamer Bot  
• Language: Python3  
• Library: Pyrogram  
• Hosted on: Railway  
• Developer: [Siam (TechifyRahul)](https://t.me/TechifyRahul)
"""

    DONATE_TXT = """
**Support the Developer:**

If you like this bot, consider supporting:

• UPI: `siam@ybl`  
• PayPal: _Coming Soon_
"""

    SEND_METADATA = "**Send metadata (e.g., Title, Artist, etc.).**"
    PREFIX = "**Send a prefix to add before the filename.**"
    SUFFIX = "**Send a suffix to add after the filename.**"
    CAPTION_TXT = "**Send a custom caption (use {filename} to include filename).**"
    THUMBNAIL_TXT = "**Send an image to set as thumbnail.**"


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

    # Admin log
    ADMIN_ID = int(Config.OWNER_ID)
    try:
        await client.send_message(
            ADMIN_ID,
            f"New user started the bot:\n\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username if user.username else 'N/A'}\n"
            f"ID: `{user.id}`\n"
            f"Profile: tg://user?id={user.id}"
        )
    except Exception as e:
        print(f"[ERROR] Couldn’t notify admin: {e}")


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
        return await message.reply_text("**Usage:** `/set_watermark your_text`")
    text = message.text.split(None, 1)[1]
    await set_watermark(message.from_user.id, text)
    await message.reply_text(f"✅ Watermark saved: `{text}`")


@Client.on_message(filters.private & filters.command("del_watermark"))
async def remove_watermark(client, message: Message):
    await del_watermark(message.from_user.id)
    await message.reply_text("🗑️ Watermark removed successfully.")