from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageEnhance
import os
import subprocess

# Extract high-quality thumbnail from middle of video
async def take_video_thumbnail(video_path, output_path):
    try:
        duration_cmd = ["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        midpoint = duration / 2

        thumb_cmd = [
            "ffmpeg", "-ss", str(midpoint), "-i", video_path,
            "-vframes", "1", "-q:v", "2", output_path
        ]
        subprocess.run(thumb_cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        return output_path
    except Exception as e:
        print(f"[Thumbnail] Extraction error: {e}")
        return None

# Add logo to thumbnail
async def add_logo_to_thumbnail(user_id, thumb_path):
    logo_path = "logo.png"
    if not os.path.exists(logo_path):
        return thumb_path  # No logo

    try:
        base_img = Image.open(thumb_path).convert("RGBA")
        logo_img = Image.open(logo_path).convert("RGBA")

        base_width, base_height = base_img.size
        logo_size = int(base_width * 0.1)
        logo_img = logo_img.resize((logo_size, logo_size))

        alpha = logo_img.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        logo_img.putalpha(alpha)

        position = (base_width - logo_size - 15, 15)
        base_img.paste(logo_img, position, logo_img)

        base_img.save(thumb_path)
        return thumb_path
    except Exception as e:
        print(f"[Logo] Error applying logo: {e}")
        return thumb_path


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

        # Handle video/photo separately
        if message.photo:
            thumb_path = file_path
        else:
            thumb_path = f"{file_path}_thumb.jpg"
            await take_video_thumbnail(file_path, thumb_path)

        # Add logo
        final_thumb = await add_logo_to_thumbnail(message.from_user.id, thumb_path)

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=final_thumb,
            caption="✅ Thumbnail with logo applied!"
        )
        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        # Cleanup
        os.remove(file_path)
        if not message.photo:
            os.remove(thumb_path)
        os.remove(final_thumb)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")