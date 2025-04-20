from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from helper.ffmpeg import fix_thumb, take_screen_shot, add_metadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix
from helper.database import jishubotz
from asyncio import sleep
from PIL import Image
from config import Config
import os, time, re, random, asyncio


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    ban_chk = await jishubotz.is_banned(int(message.from_user.id))
    if ban_chk:
        return await message.reply(
            "**ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ. ᴄᴏɴᴛᴀᴄᴛ @CallOwnerBot ᴛᴏ ʀᴇsᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇ!!**"
        )
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("Sorry, this bot doesn't support files larger than 2GB.")

    try:
        await message.reply_text(
            text=f"**Please Enter New Filename...**\n\n**Old File Name** :- `{filename}`",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )       
        await sleep(30)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**Please Enter New Filename**\n\n**Old File Name** :- `{filename}`",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )
    except Exception as e:
        print(f"Error in rename_start: {e}")

    await asyncio.sleep(600)
    await message.delete()

@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text 
        await message.delete() 
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
        if not "." in new_name:
            if "." in media.file_name:
                extn = media.file_name.rsplit('.', 1)[-1]
            else:
                extn = "mkv"
            new_name = new_name + "." + extn
        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 Document", callback_data="upload_document")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])
        await message.reply(
            text=f"**Select The Output File Type**\n\n**File Name :-** `{new_name}`",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
        )

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):    
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")
        
    prefix = await jishubotz.get_prefix(update.message.chat.id)
    suffix = await jishubotz.get_suffix(update.message.chat.id)
    new_name = update.message.text
    new_filename_ = new_name.split(":-")[1]

    try:
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
    except Exception as e:
        return await update.message.edit(f"Something Went Wrong Can't Set Prefix/Suffix 🥺\n\n**Error:** `{e}`")
    
    file_path = f"downloads/{update.from_user.id}/{new_filename}"
    file = update.message.reply_to_message

    try:
        if update.message.text != "🚀 Try To Download...  ⚡":
            ms = await update.message.edit("🚀 Try To Download...  ⚡")
    except Exception as e:
        print(f"Error editing message: {e}")
    
    try:
        path = await bot.download_media(
            message=file, 
            file_name=file_path, 
            progress=progress_for_pyrogram, 
            progress_args=("🚀 Downloading...  ⚡", ms, time.time())
        )                    
    except Exception as e:
        return await ms.edit(e)

    _bool_metadata = await jishubotz.get_metadata(update.message.chat.id) 
    
    if _bool_metadata:
        metadata = await jishubotz.get_metadata_code(update.message.chat.id)
        metadata_path = f"Metadata/{new_filename}"
        await add_metadata(path, metadata_path, metadata, ms)
    else:
        await ms.edit("⏳ Mode Changing...  ⚡")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()   
    except:
        pass
        
    ph_path = None
    user_id = int(update.message.chat.id) 
    user_name = update.message.chat.first_name
    media = getattr(file, file.media.value)
    c_caption = await jishubotz.get_caption(update.message.chat.id)
    c_thumb = await jishubotz.get_thumbnail(update.message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(text=f"Your Caption Error: ({e})")             
    else:
        caption = f"**{new_filename}**\n\n**User:** {user_name}\n**User ID:** {user_id}"

    if (media.thumbs or c_thumb):
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
            width, height, ph_path = await fix_thumb(ph_path)
        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
            except Exception as e:
                ph_path = None
                print(e)  

    try:
        if update.message.text != "💠 Try To Upload...  ⚡":
            await ms.edit("💠 Try To Upload...  ⚡")
    except Exception as e:
        print(f"Error editing message: {e}")
    
    type = update.data.split("_")[1]
    try:
        if type == "document":
            sent_message = await bot.send_document(
                update.message.chat.id,
                document=metadata_path if _bool_metadata else file_path,
                thumb=ph_path, 
                caption=caption, 
                progress=progress_for_pyrogram,
                progress_args=("💠 Uploading...  ⚡", ms, time.time())
            )
        elif type == "video": 
            sent_message = await bot.send_video(
                update.message.chat.id,
                video=metadata_path if _bool_metadata else file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("💠 Uploading...  ⚡", ms, time.time())
            )
        elif type == "audio": 
            sent_message = await bot.send_audio(
                update.message.chat.id,
                audio=metadata_path if _bool_metadata else file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("💠 Uploading...  ⚡", ms, time.time())
            )

        forwarded_message = await bot.forward_messages(
            Config.BIN_CHANNEL, 
            update.message.chat.id, 
            sent_message.id
        )

        deletion_msg = await sent_message.reply(
            text="**🗑 This file will auto-delete in 30 minutes. Save it now!**",
        )

    except Exception as e:          
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)
        return await ms.edit(f"**Error:** `{e}`")    

    await ms.delete() 
    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)

    await asyncio.sleep(1800)
    try:
        await sent_message.delete()
        await forwarded_message.delete()
        await deletion_msg.delete()
    except Exception as e:
        print(f"Error deleting messages after 30 minutes: {e}")








#chatgpt


from helper.database import get_batch_mode
from pyrogram.types import Message
from pyrogram import Client, filters

# A dict to temporarily store queued files per user
batch_queues = {}

@Client.on_message(filters.document | filters.video | filters.audio)
async def handle_file_upload(client: Client, message: Message):
    user_id = message.from_user.id
    batch_mode = await get_batch_mode(user_id)

    if batch_mode:
        if user_id not in batch_queues:
            batch_queues[user_id] = []
        
        batch_queues[user_id].append(message)

        await message.reply_text(
            f"📥 File received and queued.\nYou have **{len(batch_queues[user_id])}** files in queue.\n\nSend `/batchdone` when you're ready to rename/upload."
        )
    else:
        # Process file immediately as usual (your existing logic here)
        await process_single_file(client, message)

# New command to trigger processing of all queued files
@Client.on_message(filters.command("batchdone"))
async def process_batch_files(client: Client, message: Message):
    user_id = message.from_user.id
    files = batch_queues.get(user_id)

    if not files:
        return await message.reply_text("⚠️ You don’t have any files in batch queue.")

    await message.reply_text(f"✅ Starting to process {len(files)} files...")

    for msg in files:
        try:
            await process_single_file(client, msg)
        except Exception as e:
            await message.reply_text(f"❌ Failed to process one file: `{e}`")

    batch_queues[user_id] = []  # Clear the queue after processing