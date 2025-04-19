from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image
import os

@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def viewthumb(client, message):    
    thumb = await jishubotz.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("**You don't have any thumbnail ❌**") 

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def removethumb(client, message):
    await jishubotz.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**Thumbnail deleted successfully 🗑️**")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    mkn = await message.reply_text("Processing Thumbnail...")

    try:
        photo = await message.download()
        logo_path = "logo.png"
        thumb = Image.open(photo).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        thumb = thumb.resize((400, 300))
        logo = logo.resize((100, 100))  # Size of your logo

        thumb.paste(logo, (thumb.width - 110, thumb.height - 110), logo)

        output_path = f"thumb_{message.from_user.id}.png"
        thumb.save(output_path)

        thumb_file = await client.save_file(output_path)
        await jishubotz.set_thumbnail(message.from_user.id, file_id=thumb_file.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo)
        os.remove(output_path)
    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")