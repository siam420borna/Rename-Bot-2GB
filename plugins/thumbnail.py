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
        await message.reply_text("**তোমার কোনো থাম্বনেইল সেট করা নেই ❌**") 

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def removethumb(client, message):
    await jishubotz.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**থাম্বনেইল সফলভাবে ডিলিট করা হয়েছে 🗑️**")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    mkn = await message.reply_text("থাম্বনেইল প্রসেস করা হচ্ছে...")

    try:
        photo_path = await message.download()
        logo_path = "logo.png"

        # Open user image and logo
        thumb = Image.open(photo_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        # Resize logo to 15% of thumbnail width
        logo_width = int(thumb.width * 0.2)
        aspect_ratio = logo.height / logo.width
        logo_height = int(logo_width * aspect_ratio)
        logo = logo.resize((logo_width, logo_height))

        # Paste logo to bottom-right corner
        position = (thumb.width - logo_width - 10, thumb.height - logo_height - 10)
        thumb.paste(logo, position, logo)

        output_path = f"thumb_{message.from_user.id}.png"
        thumb.save(output_path)

        # Upload processed thumbnail
        thumb_file = await client.save_file(output_path)
        await jishubotz.set_thumbnail(message.from_user.id, file_id=thumb_file.file_id)
        await mkn.edit("**থাম্বনেইল সফলভাবে সংরক্ষণ হয়েছে ✅**")

        os.remove(photo_path)
        os.remove(output_path)
    except Exception as e:
        await mkn.edit(f"❌ থাম্বনেইল প্রসেস করতে ব্যর্থ।\nError: `{e}`")