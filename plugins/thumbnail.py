from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
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

        main_image = Image.open(photo_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize logo (10% of image width)
        main_width, main_height = main_image.size
        logo_size = int(main_width * 0.1)
        logo = logo.resize((logo_size, logo_size))

        # Reduce logo opacity
        alpha = logo.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        logo.putalpha(alpha)

        # Paste logo
        logo_pos = (15, 15)
        main_image.paste(logo, logo_pos, logo)

        # Draw text
        draw = ImageDraw.Draw(main_image)
        font_path = "arial.ttf"  # Make sure this font file exists
        font = ImageFont.truetype(font_path, size=int(logo_size * 0.35))
        text = "@YourChannelName"
        text_pos = (logo_pos[0] + logo_size + 10, logo_pos[1] + int(logo_size * 0.25))
        draw.text(text_pos, text, fill=(255, 255, 255, 180), font=font)

        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path, "PNG")

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo and channel name applied!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")