from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageEnhance
import os
import subprocess

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

@Client.on_message(filters.private & (filters.photo | filters.video))
async def addthumbs(client, message):
    mkn = await message.reply_text("Processing thumbnail...")

    try:
        file_path = await message.download(file_name=f"{message.from_user.id}_temp")

        # If it's a video, extract a high-res thumbnail
        if message.photo:
            thumb_path = file_path
        else:
            thumb_path = f"{file_path}_thumb.jpg"
            cmd = [
                "ffmpeg", "-i", file_path,
                "-ss", "00:00:01.000", "-vframes", "1",
                "-vf", "scale=1280:-1",
                thumb_path
            ]
            subprocess.run(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        # Open image and logo
        main_image = Image.open(thumb_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize logo (10% of width)
        main_width, main_height = main_image.size
        logo_size = int(main_width * 0.1)
        logo = logo.resize((logo_size, logo_size))

        # Transparent logo (60% opacity)
        alpha = logo.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        logo.putalpha(alpha)

        # Top-right position
        position = (main_width - logo_size - 15, 15)
        main_image.paste(logo, position, logo)

        # Save final image
        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path, "PNG")

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo applied!"
        )
        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        # Cleanup
        os.remove(file_path)
        if not message.photo:
            os.remove(thumb_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")