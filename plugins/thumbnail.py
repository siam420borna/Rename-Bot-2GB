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
    mkn = await message.reply_text("Processing your thumbnail...")

    try:
        photo_path = await message.download()
        logo_path = "logo.png"

        thumb = Image.open(photo_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        logo_width = int(thumb.width * 0.2)
        aspect_ratio = logo.height / logo.width
        logo_height = int(logo_width * aspect_ratio)
        logo = logo.resize((logo_width, logo_height))

        position = (thumb.width - logo_width - 10, thumb.height - logo_height - 10)
        thumb.paste(logo, position, logo)

        output_path = f"thumb_{message.from_user.id}.png"
        thumb.save(output_path)

        # Upload and get file_id from the sent message
        sent = await client.send_photo(chat_id=message.chat.id, photo=output_path, caption="Thumbnail preview with logo.")
        file_id = sent.photo.file_id

        await jishubotz.set_thumbnail(message.from_user.id, file_id=file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")