from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image

import os

LOGO_PATH = "logo.png"

def add_watermark(original_path):
    base = Image.open(original_path).convert("RGBA")
    watermark = Image.open(LOGO_PATH).convert("RGBA")

    # Resize watermark (optional)
    ratio = min(base.size[0] // 5 / watermark.size[0], base.size[1] // 5 / watermark.size[1])
    wm_size = (int(watermark.size[0] * ratio), int(watermark.size[1] * ratio))
    watermark = watermark.resize(wm_size, Image.ANTIALIAS)

    # Position: bottom-right
    position = (base.size[0] - wm_size[0] - 10, base.size[1] - wm_size[1] - 10)

    transparent = Image.new('RGBA', base.size)
    transparent.paste(base, (0, 0))
    transparent.paste(watermark, position, mask=watermark)
    final = transparent.convert("RGB")

    final_path = "watermarked_thumb.jpg"
    final.save(final_path, "JPEG")
    return final_path

@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def viewthumb(client, message):    
    thumb = await jishubotz.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("**You Don't Have Any Thumbnail ❌**") 

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def removethumb(client, message):
    await jishubotz.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**Thumbnail Deleted Successfully 🗑️**")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    msg = await message.reply_text("Processing Thumbnail...")

    downloaded_path = await message.download()
    watermarked_path = add_watermark(downloaded_path)

    thumb_msg = await client.send_photo(
        chat_id=message.chat.id,
        photo=watermarked_path,
        caption="✅ Thumbnail with watermark saved!"
    )

    await jishubotz.set_thumbnail(message.from_user.id, file_id=thumb_msg.photo.file_id)
    await msg.delete()

    os.remove(downloaded_path)
    os.remove(watermarked_path)