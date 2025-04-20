import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode
from helper.database import jishubotz, total_users
from config import Config, Txt  


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await jishubotz.add_user(client, message)  
    count = await total_users()      
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton('ℹ️ ᴀʙᴏᴜᴛ', callback_data='about'),
         InlineKeyboardButton('❓ ʜᴇʟᴘ', callback_data='help')],
        [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://telegram.me/TechifyRahul')]
    ])
    start_caption = Txt.START_TXT.format(user.mention) + f"\n\n👥 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{count}</code>"
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=start_caption, reply_markup=button, parse_mode=ParseMode.HTML)       
    else:
        await message.reply_text(text=start_caption, reply_markup=button, parse_mode=ParseMode.HTML, disable_web_page_preview=True)



@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":
        count = await total_users()
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention) + f"\n\n👥 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{count}</code>",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('ℹ️ ᴀʙᴏᴜᴛ', callback_data='about'),
                 InlineKeyboardButton('❓ ʜᴇʟᴘ', callback_data='help')],
                [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://telegram.me/TechifyRahul')]
            ])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛠️ sᴇᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data = "meta")],
                [InlineKeyboardButton("🔠 ᴘʀᴇꜰɪx", callback_data = "prefix"),
                 InlineKeyboardButton("🔡 sᴜꜰꜰɪx", callback_data = "suffix")],
                [InlineKeyboardButton("✏️ ᴄᴀᴘᴛɪᴏɴ", callback_data = "caption"),
                 InlineKeyboardButton("🖼️ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data = "thumbnail")],
                [InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data = "start")]
            ])            
        )

    elif data == "meta":
        await query.message.edit_caption(
            caption=Txt.SEND_METADATA,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "prefix":
        await query.message.edit_caption(
            caption=Txt.PREFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "suffix":
        await query.message.edit_caption(
            caption=Txt.SUFFIX,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "caption":
        await query.message.edit_caption(
            caption=Txt.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "thumbnail":
        await query.message.edit_caption(
            caption=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 ʀᴇᴘᴏ", url="https://github.com/TechifyBots"),
                 InlineKeyboardButton("💥 ᴅᴏɴᴀᴛᴇ", callback_data="donate")],
                [InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="start")]
            ])            
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ᴍᴏʀᴇ ʙᴏᴛs", url="https://telegram.me/TechifyBots/8")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data = "about"),
                 InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data = "close")]
            ])            
        )

    elif data == "close":
        try:
            await query.message.edit("❌ ᴄʟᴏsᴇᴅ ʙʏ ᴜsᴇʀ. ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ!")
            await query.message.continue_propagation()
        except:
            pass