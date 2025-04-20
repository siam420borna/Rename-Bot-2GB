from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageDraw, ImageFont
import os

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    mkn = await message.reply_text("Processing thumbnail...")

    try:
        photo_path = await message.download(file_name=f"{message.from_user.id}_original.jpg")

        image = Image.open(photo_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Smaller logo like TV logo
        logo = logo.resize((35, 35))  # <- TV style size

        # Paste logo at top-left with margin
        image.paste(logo, (10, 10), logo)

        # Channel name text beside logo
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 18)
        text = "@YourChannelName"
        draw.text((55, 15), text, font=font, fill=(255, 255, 255, 255))  # beside logo

        # Resize to Telegram thumbnail size
        final_thumb = image.resize((400, 300))

        output_path = f"thumb_{message.from_user.id}.png"
        final_thumb.save(output_path)

        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with TV-style logo & channel name!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")