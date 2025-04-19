from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageEnhance
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
    mkn = await message.reply_text("Processing thumbnail...")

    try:
        photo_path = await message.download(file_name=f"{message.from_user.id}_original.jpg")

        # Open main image and logo
        main_image = Image.open(photo_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize logo to small TV-style (10% of width)
        main_width, main_height = main_image.size
        logo_size = int(main_width * 0.1)  # 10% of image width
        logo = logo.resize((logo_size, logo_size))

        # Add transparency
        alpha = logo.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)  # 60% opacity
        logo.putalpha(alpha)

        # Paste at top-left
        position = (15, 15)
        main_image.paste(logo, position, logo)

        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path, "PNG")

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo applied!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")