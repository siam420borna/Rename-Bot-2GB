from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from helper.database import jishubotz
from config import Config, Txt
from helper.database import set_watermark, get_watermark, del_watermark


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await jishubotz.add_user(client, message)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about"),
         InlineKeyboardButton("• ʜᴇʟᴘ •", callback_data="help")],
        [InlineKeyboardButton("♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻", url="https://t.me/TechifyRahul")]
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
        await message.reply_text(f"Error in /start: {e}")


@Client.on_callback_query()
async def callback(client, query: CallbackQuery):
    data = query.data
    user = query.from_user

    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about"),
                 InlineKeyboardButton("• ʜᴇʟᴘ •", callback_data="help")],
                [InlineKeyboardButton("♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻", url="https://t.me/TechifyRahul")]
            ])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("sᴇᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data="meta")],
                [InlineKeyboardButton("ᴘʀᴇꜰɪx", callback_data="prefix"),
                 InlineKeyboardButton("sᴜꜰꜰɪx", callback_data="suffix")],
                [InlineKeyboardButton("ᴄᴀᴘᴛɪᴏɴ", callback_data="caption"),
                 InlineKeyboardButton("ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="thumbnail")],
                [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start")]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 ʀᴇᴘᴏ", url="https://github.com/TechifyBots"),
                 InlineKeyboardButton("💥 ᴅᴏɴᴀᴛᴇ", callback_data="donate")],
                [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start")]
            ])
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ᴍᴏʀᴇ ʙᴏᴛs", url="https://t.me/TechifyBots/8")],
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="about"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "meta":
        await query.message.edit_text(
            text=Txt.SEND_METADATA,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "prefix":
        await query.message.edit_text(
            text=Txt.PREFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "suffix":
        await query.message.edit_text(
            text=Txt.SUFFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "thumbnail":
        await query.message.edit_text(
            text=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
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