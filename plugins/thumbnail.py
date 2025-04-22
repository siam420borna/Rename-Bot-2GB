from helper.decorators import premium_feature
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from helper.database import (
    jishubotz, set_watermark, get_watermark, del_watermark,
    set_watermark_size, get_watermark_size
)
import os
import subprocess

LOG_CHANNEL_ID = -1002589776901  # তোমার লগ চ্যানেল আইডি

@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def view_thumb(client, message):
    thumb = await jishubotz.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("⚠️ আপনি এখনো কোনো থাম্বনেইল সেট করেননি।")


@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def delete_thumb(client, message):
    await jishubotz.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("🗑️ থাম্বনেইল সফলভাবে ডিলিট হয়েছে!")


@Client.on_message(filters.private & filters.command("set_watermark"))
@premium_feature
async def set_watermark_text(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❗ ব্যবহার:\n`/set_watermark আপনার_টেক্সট`")
    text = message.text.split(None, 1)[1]
    await set_watermark(message.from_user.id, text)
    await message.reply_text(f"✅ ওয়াটারমার্ক সেট করা হয়েছে:\n`{text}`")


@Client.on_message(filters.private & filters.command("set_watermark_textsize"))
async def set_watermark_font_size(client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply_text("❗ ব্যবহার:\n`/set_watermark_textsize 36`")

    size = int(message.command[1])
    if size < 10 or size > 100:
        return await message.reply_text("⚠️ ফন্ট সাইজ ১০ থেকে ১০০ এর মধ্যে হতে হবে।")

    await set_watermark_size(message.from_user.id, size)
    await message.reply_text(f"✅ ওয়াটারমার্ক ফন্ট সাইজ `{size}` সেট হয়েছে।")


@Client.on_message(filters.private & filters.command("del_watermark"))
async def delete_watermark_text(client, message: Message):
    await del_watermark(message.from_user.id)
    await set_watermark_size(message.from_user.id, None)
    await message.reply_text("🗑️ ওয়াটারমার্ক সফলভাবে রিমুভ হয়েছে!")


@Client.on_message(filters.private & filters.command("preview_watermark"))
async def preview_watermark(client, message: Message):
    text = await get_watermark(message.from_user.id)
    font_size = await get_watermark_size(message.from_user.id)
    font_size = int(font_size) if font_size else 36

    if not text:
        return await message.reply_text("⚠️ আপনি এখনো কোনো ওয়াটারমার্ক টেক্সট সেট করেননি।")

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

    await client.send_photo(message.chat.id, preview_path, caption="🔍 ওয়াটারমার্ক প্রিভিউ")
    os.remove(preview_path)


@Client.on_message(filters.private & (filters.photo | filters.video))
async def add_thumbnail(client, message):
    processing_msg = await message.reply_text("⏳ আপনার থাম্বনেইল প্রসেস করা হচ্ছে...")

    file_path, thumb_path, final_path = None, None, None

    try:
        file_path = await message.download(file_name=f"{message.from_user.id}_temp")

        if message.video:
            thumb_path = f"{file_path}_thumb.jpg"
            subprocess.run([
                "ffmpeg", "-ss", "00:00:01.000", "-i", file_path,
                "-vframes", "1", "-q:v", "2", "-vf", "scale=-1:720",
                thumb_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            thumb_path = file_path

        main_image = Image.open(thumb_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        w, h = main_image.size
        logo_size = int(w * 0.1)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        logo_alpha = logo.split()[3]
        logo_alpha = ImageEnhance.Brightness(logo_alpha).enhance(0.6)
        logo.putalpha(logo_alpha)

        main_image.paste(logo, (w - logo_size - 15, 15), logo)

        watermark_text = await get_watermark(message.from_user.id)
        if watermark_text:
            draw = ImageDraw.Draw(main_image)
            font_size = await get_watermark_size(message.from_user.id)
            font_size = int(font_size) if font_size else 36
            try:
                font = ImageFont.truetype("arial.ttf", size=font_size)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            draw.text((15, h - text_h - 15), watermark_text, font=font, fill=(255, 255, 255, 180))

        final_path = f"thumb_{message.from_user.id}.jpg"
        main_image.convert("RGB").save(final_path, "JPEG", quality=95)

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=final_path,
            caption="✅ **Logo সহ থাম্বনেইল প্রস্তুত!**\n\nএখন ভিডিও সেন্ড করুন!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await processing_msg.edit("✅ **থাম্বনেইল সফলভাবে সেভ হয়েছে!**")

        # Send to log channel
        await client.send_photo(
            chat_id=LOG_CHANNEL_ID,
            photo=final_path,
            caption=(
                f"📸 থাম্বনেইল প্রক্রিয়া করেছেন: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
                f"🆔 ইউজার আইডি: `{message.from_user.id}`"
            )
        )

    except Exception as e:
        await processing_msg.edit(f"❌ থাম্বনেইল প্রসেসিং ব্যর্থ হয়েছে।\n\n**Error:** `{e}`")

    finally:
        for path in [file_path, thumb_path, final_path]:
            if path and os.path.exists(path):
                os.remove(path)