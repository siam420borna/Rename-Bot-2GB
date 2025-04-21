from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from helper.database import (
    jishubotz, set_watermark, get_watermark, del_watermark,
    set_watermark_size, get_watermark_size
)
import os
import subprocess


@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def view_thumb(client, message):
    thumb = await jishubotz.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("⚠️ You don't have any thumbnail set yet.")


@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def delete_thumb(client, message):
    await jishubotz.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("🗑️ Thumbnail deleted successfully!")


@Client.on_message(filters.private & filters.command("set_watermark"))
async def set_watermark_text(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage:\n`/set_watermark YourTextHere`")
    text = message.text.split(None, 1)[1]
    await set_watermark(message.from_user.id, text)
    await message.reply_text(f"✅ Watermark set to:\n`{text}`")


@Client.on_message(filters.private & filters.command("set_watermark_textsize"))
async def set_watermark_font_size(client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply_text("❗ Usage:\n`/set_watermark_textsize 36`")

    size = int(message.command[1])
    if size < 10 or size > 100:
        return await message.reply_text("⚠️ Font size must be between 10 and 100.")

    await set_watermark_size(message.from_user.id, size)
    await message.reply_text(f"✅ Watermark text size set to `{size}`")


@Client.on_message(filters.private & filters.command("del_watermark"))
async def delete_watermark_text(client, message: Message):
    await del_watermark(message.from_user.id)
    await set_watermark_size(message.from_user.id, None)
    await message.reply_text("🗑️ Watermark removed successfully!")


@Client.on_message(filters.private & filters.command("preview_watermark"))
async def preview_watermark(client, message: Message):
    text = await get_watermark(message.from_user.id)
    font_size = await get_watermark_size(message.from_user.id) or 36

    if not text:
        return await message.reply_text("⚠️ You haven't set any watermark text yet.")

    image = Image.new("RGBA", (720, 150), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pos = ((720 - text_w) // 2, (150 - text_h) // 2)
    draw.text(pos, text, font=font, fill=(255, 255, 255, 200))

    preview_path = f"preview_{message.from_user.id}.png"
    image.save(preview_path)

    await client.send_photo(message.chat.id, preview_path, caption="🔍 Watermark preview")
    os.remove(preview_path)


@Client.on_message(filters.private & (filters.photo | filters.video))
async def add_thumbnail(client, message):
    processing_msg = await message.reply_text("⏳ Processing your thumbnail...")

    try:
        file_path = await message.download(file_name=f"{message.from_user.id}_temp")

        # Generate thumbnail for video
        if message.video:
            thumb_path = f"{file_path}_thumb.jpg"
            subprocess.run([
                "ffmpeg", "-ss", "00:00:01.000", "-i", file_path,
                "-vframes", "1", "-q:v", "2", "-vf", "scale=-1:720",
                thumb_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            thumb_path = file_path

        # Open image and logo
        main_image = Image.open(thumb_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize and fade logo
        w, h = main_image.size
        logo_size = int(w * 0.1)
        logo = logo.resize((logo_size, logo_size))
        alpha = ImageEnhance.Brightness(logo.split()[3]).enhance(0.6)
        logo.putalpha(alpha)
        main_image.paste(logo, (w - logo_size - 15, 15), logo)

        # Watermark text
        watermark_text = await get_watermark(message.from_user.id)
        if watermark_text:
            draw = ImageDraw.Draw(main_image)
            font_size = await get_watermark_size(message.from_user.id) or 36
            try:
                font = ImageFont.truetype("arial.ttf", size=font_size)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            draw.text((15, h - text_h - 15), watermark_text, font=font, fill=(255, 255, 255, 180))

        # Save and send
        final_path = f"thumb_{message.from_user.id}.jpg"
        main_image.convert("RGB").save(final_path, "JPEG", quality=95)

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=final_path,
            caption="✅ **Thumbnail with logo added!**\n\nNow send your video to apply it!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await processing_msg.edit("✅ **Thumbnail saved successfully!**")

    except Exception as e:
        await processing_msg.edit(f"❌ Failed to process thumbnail.\n\n**Error:** `{e}`")

    finally:
        for path in [file_path, thumb_path, final_path]:
            if os.path.exists(path):
                os.remove(path)



# Example DB: key-value storage like MongoDB or SQLite

async def set_watermark_size(user_id, size):
    # Update or delete font size
    if size:
        # Save in DB (example: await db.update({"_id": user_id}, {"$set": {"font_size": size}}))
        pass
    else:
        # Remove (example: await db.update({"_id": user_id}, {"$unset": {"font_size": ""}}))
        pass

async def get_watermark_size(user_id):
    # Fetch from DB (example: user = await db.find_one({"_id": user_id}); return user.get("font_size"))
    return 36  # Default fallback