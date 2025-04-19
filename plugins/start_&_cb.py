import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from helper.database import jishubotz
from config import Config, Txt


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    is_new = await jishubotz.add_user(client, message)  # True if first time start
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton('• ᴀʙᴏᴜᴛ •', callback_data='about'),
         InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='help')],
        [InlineKeyboardButton("♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻", url='https://telegram.me/TechifyRahul')]
    ])
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=buttons)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=buttons, disable_web_page_preview=True)

    if is_new:
        log_text = (
            f"**New User Started Bot**\n\n"
            f"**ID:** `{user.id}`\n"
            f"**Name:** {user.first_name or 'N/A'}\n"
            f"**Username:** @{user.username if user.username else 'N/A'}\n"
            f"**Mention:** {user.mention}\n"
            f"**DC ID:** `{user.dc_id if hasattr(user, 'dc_id') else 'N/A'}`"
        )
        try:
            await client.send_message(-1002589776901, log_text)
        except Exception as e:
            print(f"Error sending log: {e}")


@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user_mention = query.from_user.mention

    async def send_caption(caption_text):
        await query.message.edit_caption(
            caption=caption_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(user_mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('• ᴀʙᴏᴜᴛ •', callback_data='about'),
                 InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='help')],
                [InlineKeyboardButton("♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻", url='https://telegram.me/TechifyRahul')]
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

    elif data in ["meta", "prefix", "suffix", "caption", "thumbnail"]:
        captions = {
            "meta": Txt.SEND_METADATA,
            "prefix": Txt.PREFIX,
            "suffix": Txt.SUFFIX,
            "caption": Txt.CAPTION_TXT,
            "thumbnail": Txt.THUMBNAIL_TXT
        }
        await send_caption(captions[data])

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻  ʀᴇᴘᴏ", url="https://github.com/TechifyBots"),
                 InlineKeyboardButton("💥  ᴅᴏɴᴀᴛᴇ", callback_data="donate")],
                [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start")]
            ])
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ᴍᴏʀᴇ ʙᴏᴛs", url="https://telegram.me/TechifyBots/8")],
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="about"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()

    elif data.startswith("sendAlert") or data.startswith("sendUnbanAlert"):
        parts = data.split("_")
        if len(parts) >= 2:
            user_id = parts[1]
            reason = parts[2] if len(parts) > 2 else ""
            try:
                uid = int(user_id.strip())
                if data.startswith("sendAlert"):
                    msg = f"<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ʙʏ [ʀᴀʜᴜʟ](https://telegram.me/callownerbot)\nʀᴇᴀsᴏɴ : {reason}</b>"
                    await client.send_message(uid, msg)
                    await query.message.edit(f"<b>Aʟᴇʀᴛ sᴇɴᴛ ᴛᴏ <code>{uid}</code>\nʀᴇᴀsᴏɴ : {reason}</b>")
                else:
                    msg = "<b>ʜᴜʀʀᴀʏ..ʏᴏᴜ ᴀʀᴇ ᴜɴʙᴀɴɴᴇᴅ ʙʏ [ʀᴀʜᴜʟ](https://telegram.me/callownerbot)</b>"
                    await client.send_message(uid, msg)
                    await query.message.edit(f"<b>Uɴʙᴀɴɴᴇᴅ Aʟᴇʀᴛ sᴇɴᴛ ᴛᴏ <code>{uid}</code>\nᴀʟᴇʀᴛ ᴛᴇxᴛ : {msg}</b>")
            except Exception as e:
                await query.message.edit(f"<b>sʀʏ ɪ ɢᴏᴛ ᴛʜɪs ᴇʀʀᴏʀ : {e}</b>")
        else:
            await query.message.edit("<b>Invalid format. Unable to process the request.</b>")

    elif data.startswith("noAlert") or data.startswith("NoUnbanAlert"):
        parts = data.split("_")
        if len(parts) == 2:
            try:
                uid = int(parts[1].strip())
                action = "ʙᴀɴ" if data.startswith("noAlert") else "ᴜɴʙᴀɴ"
                await query.message.edit(f"<b>Tʜᴇ {action} ᴏɴ <code>{uid}</code> ᴡᴀs ᴇxᴇᴄᴜᴛᴇᴅ sɪʟᴇɴᴛʟʏ.</b>")
            except:
                await query.message.edit("<b>Invalid user ID format.</b>")