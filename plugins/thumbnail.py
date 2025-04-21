import os
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageDraw, ImageFont
from config import Config
from helper.database import jishubotz

# Set Watermark Text
@Client.on_message(filters.command("setwatermark") & filters.private)
async def set_watermark_text(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("দয়া করে ওয়াটারমার্ক লেখাটি দিন।\n\nউদাহরণ: `/setwatermark JishuBotz`")
    text = m.text.split(" ", 1)[1]
    await jishubotz.set_watermark_text(m.from_user.id, text)
    await m.reply("✅ ওয়াটারমার্ক সেট করা হয়েছে।")

# Set Watermark Font Size
@Client.on_message(filters.command("setsize") & filters.private)
async def set_watermark_size(_, m: Message):
    if len(m.command) < 2 or not m.command[1].isdigit():
        return await m.reply("দয়া করে ফন্ট সাইজ দিন (সংখ্যা)।\n\nউদাহরণ: `/setsize 40`")
    size = int(m.command[1])
    await jishubotz.set_watermark_size(m.from_user.id, size)
    await m.reply(f"✅ ফন্ট সাইজ `{size}` সেট করা হয়েছে।")

# Upload and Set Logo Image
@Client.on_message(filters.command("setlogo") & filters.private & filters.photo)
async def set_logo(_, m: Message):
    path = f"downloads/{m.from_user.id}_logo.jpg"
    await m.download(path)
    await jishubotz.set_logo(m.from_user.id, path)
    await m.reply("✅ লোগো সেভ করা হয়েছে।")

# Upload and Set Thumbnail Image
@Client.on_message(filters.command("thumb") & filters.private & filters.photo)
async def set_thumb(_, m: Message):
    path = f"downloads/{m.from_user.id}_thumb.jpg"
    await m.download(path)
    await jishubotz.set_thumbnail(m.from_user.id, path)
    await m.reply("✅ থাম্বনেইল সেভ করা হয়েছে।")

# Clear Thumbnail, Logo & Watermark Settings
@Client.on_message(filters.command("clearthumb") & filters.private)
async def clear_thumb(_, m: Message):
    await jishubotz.clear_thumbnail(m.from_user.id)
    await m.reply("🗑️ থাম্বনেইল সেটিংস রিসেট হয়েছে।")

# Main Function: Apply Watermark Text + Logo on Thumbnail
async def add_watermark_and_logo(user_id: int, input_file: str, output_file: str):
    wm_text = await jishubotz.get_watermark_text(user_id) or ""
    font_size = await jishubotz.get_watermark_size(user_id) or 40
    logo_path = await jishubotz.get_logo(user_id)
    thumb_path = await jishubotz.get_thumbnail(user_id)

    if not thumb_path:
        return None

    base = Image.open(thumb_path).convert("RGBA")
    txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Watermark text placement
    width, height = base.size
    text_width, text_height = draw.textsize(wm_text, font=font)
    text_position = (width - text_width - 20, height - text_height - 20)
    draw.text(text_position, wm_text, font=font, fill=(255, 255, 255, 180))

    combined = Image.alpha_composite(base, txt_layer)

    # Paste logo if exists
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((100, 100))
        combined.paste(logo, (20, 20), logo)

    combined.convert("RGB").save(output_file, "JPEG")
    return output_file