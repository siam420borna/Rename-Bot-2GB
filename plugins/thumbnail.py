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

        # Load main image and logo
        main_image = Image.open(photo_path).convert("RGBA")
        logo = Image.open("logo.png").convert("RGBA")

        # Resize both if needed
        main_image = main_image.resize((400, 300))
        logo = logo.resize((100, 100))

        # Paste logo onto the thumbnail
        main_image.paste(logo, (main_image.width - 110, main_image.height - 110), logo)

        output_path = f"thumb_{message.from_user.id}.png"
        main_image.save(output_path)

        # Upload image to Telegram and get file_id
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=output_path,
            caption="✅ Thumbnail with logo applied!"
        )

        await jishubotz.set_thumbnail(message.from_user.id, file_id=sent.photo.file_id)
        await mkn.edit("**Thumbnail saved successfully ✅**")

        # Clean up
        os.remove(photo_path)
        os.remove(output_path)

    except Exception as e:
        await mkn.edit(f"❌ Failed to process thumbnail.\nError: `{e}`")