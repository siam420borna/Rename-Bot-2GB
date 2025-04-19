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
        await message.reply_text("**You don't have any thumbnail ❌**") 

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def removethumb(client, message):
    await jishubotz.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**Thumbnail deleted successfully 🗑️**")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    mkn = await message.reply_text("Processing thumbnail...")

    try:
        # Download the photo
        photo_path = await message.download(file_name=f"{message.from_user.id}_original.jpg")

        # Open main image and logo
        main_image = Image.open(photo_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize logo only if it's too big (keep original image size for better quality)
        main_width, main_height = main_image.size
        logo_size = int(main_width * 0.25)  # 25% of image width
        logo = logo.resize((logo_size, logo_size))

        # Paste logo at bottom-right
        position = (main_width - logo_size - 10, main_height - logo_size - 10)
        main_image.paste(logo, position, logo)

        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path, "PNG")

        # Send back and save file_id
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo applied!"
        )

        # Save file_id for future use
        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        # Cleanup
        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")