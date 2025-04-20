from pyrogram import Client, filters
from helper.database import jishubotz
from PIL import Image, ImageDraw, ImageFont
import os

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    mkn = await message.reply_text("Processing thumbnail...")

    try:
        # Download the photo
        photo_path = await message.download(file_name=f"{message.from_user.id}_original.jpg")

        # Load and resize main image
        main_image = Image.open(photo_path).convert("RGBA")
        main_image = main_image.resize((400, 300))

        # Load and resize logo
        logo = Image.open("logo.png").convert("RGBA")
        logo = logo.resize((40, 40))  # Small logo like TV channels

        # Paste logo (top-left corner)
        main_image.paste(logo, (10, 10), logo)

        # Draw text next to logo
        draw = ImageDraw.Draw(main_image)
        font = ImageFont.truetype("arial.ttf", 20)  # Use existing TTF font

        draw.text((60, 15), "@YourChannelName", font=font, fill="white")

        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path)

        # Send photo to Telegram & save file_id
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo and channel name added!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")