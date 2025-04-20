from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageEnhance
import os
import subprocess

@Client.on_message(filters.private & filters.video)
async def addthumbs_from_video(client, message):
    mkn = await message.reply_text("Processing high-quality thumbnail...")

    try:
        # Download video
        video_path = await message.download(file_name=f"{message.from_user.id}_video.mp4")
        thumb_path = f"{message.from_user.id}_thumb.jpg"

        # Extract frame from video using ffmpeg (1st second)
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-ss", "00:00:01.000", "-vframes", "1", thumb_path
        ], check=True)

        # Open extracted image
        main_image = Image.open(thumb_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize logo
        main_width, _ = main_image.size
        logo_size = int(main_width * 0.1)
        logo = logo.resize((logo_size, logo_size))

        # Add transparency to logo
        alpha = logo.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        logo.putalpha(alpha)

        # Paste logo top-left
        main_image.paste(logo, (15, 15), logo)

        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path, "PNG")

        # Send back for preview
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Video thumbnail created with logo!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        # Cleanup
        os.remove(video_path)
        os.remove(output_path)
        os.remove(thumb_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to create thumbnail.\nError: `{e}`")