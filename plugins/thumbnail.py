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

        # Load main image and logo
        main_image = Image.open(photo_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize main image and logo
        main_image = main_image.resize((400, 300))
        logo = logo.resize((70, 70))  # Small logo

        # Add logo to top-left
        main_image.paste(logo, (10, 10), logo)

        # Add watermark text
        draw = ImageDraw.Draw(main_image)
        font = ImageFont.truetype("arial.ttf", 20)  # Ensure this font exists
        text = "YourChannelName"
        draw.text((15, main_image.height - 30), text, font=font, fill=(255, 255, 255, 180))

        # Save the final image
        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path)

        # Upload image and get file_id
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo and watermark applied!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")