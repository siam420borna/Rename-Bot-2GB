from pyrogram import Client, filters
from helper.database import jishubotz, set_watermark, get_watermark, del_watermark
from pyrogram.types import Message
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import os
import subprocess


@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb'])) async def viewthumb(client, message):
thumb = await jishubotz.get_thumbnail(message.from_user.id) if thumb: await client.send_photo(chat_id=message.chat.id, photo=thumb) else: await message.reply_text("You don't have any thumbnail ❌")

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb'])) async def removethumb(client, message): await jishubotz.set_thumbnail(message.from_user.id, file_id=None) await message.reply_text("Thumbnail deleted successfully 🗑️")

@Client.on_message(filters.private & filters.command("set_watermark")) async def save_watermark(client, message: Message): if len(message.command) < 2: return await message.reply_text("Usage: /set_watermark YourTextHere") text = message.text.split(None, 1)[1] await set_watermark(message.from_user.id, text) await message.reply_text(f"✅ Watermark set to: {text}")

@Client.on_message(filters.private & filters.command("del_watermark")) async def remove_watermark(client, message: Message): await del_watermark(message.from_user.id) await message.reply_text("🖑️ Watermark removed.")

@Client.on_message(filters.private & (filters.photo | filters.video)) async def addthumbs(client, message): mkn = await message.reply_text("Processing thumbnail...")

try:
    file_path = await message.download(file_name=f"{message.from_user.id}_temp")

    # Determine thumbnail path
    if message.photo:
        thumb_path = file_path
    else:
        thumb_path = f"{file_path}_thumb.jpg"
        cmd = [
            "ffmpeg", "-ss", "00:00:01.000",
            "-i", file_path,
            "-vframes", "1",
            "-q:v", "2",
            "-vf", "scale=-1:720",
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

    # Add watermark text if set
    watermark_text = await get_watermark(message.from_user.id)
    if watermark_text:
        draw = ImageDraw.Draw(main_image)
        try:
            font = ImageFont.truetype("arial.ttf", size=36)
        except:
            font = ImageFont.load_default()
        text_width, text_height = draw.textsize(watermark_text, font=font)
        x = 15
        y = main_height - text_height - 15
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 180))

    # Save final image as JPEG
    output_path = f"thumb_{message.from_user.id}.jpg"
    main_image.convert("RGB").save(output_path, "JPEG", quality=95)

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

