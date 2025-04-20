import os
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    ForceReply
)
from config import Config, Txt
from helper.database import jishubotz
from helper.utils import (
    generate_random_string,
    is_valid_filename,
    get_file_extension
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# States for conversation handler
class States:
    WAITING_FILE = 0
    WAITING_NEW_NAME = 1
    WAITING_PREFIX = 2
    WAITING_SUFFIX = 3
    WAITING_CAPTION = 4

@Client.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    """Start command handler with user registration"""
    user = message.from_user
    await jishubotz.add_user(client, message)
    
    buttons = [
        [InlineKeyboardButton('• ᴀʙᴏᴜᴛ •', callback_data='about'),
         InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='help')],
        [InlineKeyboardButton("♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻", url=Config.DEVELOPER_URL)]
    ]
    
    if Config.START_PIC:
        await message.reply_photo(
            Config.START_PIC,
            caption=Txt.START_TXT.format(user.mention),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text(
            text=Txt.START_TXT.format(user.mention),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def handle_file(client: Client, message: Message):
    """Handle incoming files for renaming"""
    try:
        # Store file info in user data
        file = message.document or message.video or message.audio
        file_name = file.file_name
        file_id = file.file_id
        
        # Generate a random string for temp file naming
        temp_name = f"temp_{generate_random_string(8)}"
        
        # Store file info
        client.user_data[message.from_user.id] = {
            'file_id': file_id,
            'original_name': file_name,
            'temp_name': temp_name,
            'file_type': message.media.value
        }
        
        # Ask for new file name
        await message.reply_text(
            Txt.ASK_NEW_NAME,
            reply_markup=ForceReply(selective=True)
        )
        
        # Set state to waiting for new name
        client.user_data[message.from_user.id]['state'] = States.WAITING_NEW_NAME
        
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await message.reply_text(Txt.ERROR_GENERIC)

@Client.on_message(filters.private & filters.reply)
async def handle_reply(client: Client, message: Message):
    """Handle user replies (new filename, prefix, suffix)"""
    user_id = message.from_user.id
    user_data = client.user_data.get(user_id, {})
    
    if not user_data:
        return
    
    current_state = user_data.get('state')
    
    if current_state == States.WAITING_NEW_NAME:
        # Process new filename
        new_name = message.text.strip()
        
        if not is_valid_filename(new_name):
            await message.reply_text(Txt.INVALID_FILENAME)
            return
        
        # Add extension if missing
        original_ext = os.path.splitext(user_data['original_name'])[1]
        if not os.path.splitext(new_name)[1]:
            new_name += original_ext
        
        user_data['new_name'] = new_name
        
        # Ask if user wants to add prefix/suffix
        buttons = [
            [InlineKeyboardButton("➕ ᴘʀᴇꜰɪx", callback_data="add_prefix"),
             InlineKeyboardButton("➕ sᴜꜰꜰɪx", callback_data="add_suffix")],
            [InlineKeyboardButton("⏩ sᴋɪᴘ", callback_data="skip_modifiers")]
        ]
        
        await message.reply_text(
            Txt.ASK_MODIFIERS,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        user_data['state'] = States.WAITING_PREFIX
        
    elif current_state == States.WAITING_PREFIX:
        # Process prefix
        user_data['prefix'] = message.text.strip()
        await message.reply_text(
            Txt.PREFIX_ADDED.format(user_data['prefix']),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ᴄᴏɴᴛɪɴᴜᴇ", callback_data="process_file")]
            ])
        )
        
    elif current_state == States.WAITING_SUFFIX:
        # Process suffix
        user_data['suffix'] = message.text.strip()
        await message.reply_text(
            Txt.SUFFIX_ADDED.format(user_data['suffix']),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ᴄᴏɴᴛɪɴᴜᴇ", callback_data="process_file")]
            ])
        )

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    """Handle all callback queries"""
    data = query.data
    user_id = query.from_user.id
    user_data = client.user_data.get(user_id, {})
    
    if data == "start":
        await handle_start_callback(query)
    
    elif data == "help":
        await handle_help_callback(query)
    
    elif data == "about":
        await handle_about_callback(query)
    
    elif data == "add_prefix":
        await query.message.edit_text(Txt.ASK_PREFIX)
        client.user_data[user_id]['state'] = States.WAITING_PREFIX
    
    elif data == "add_suffix":
        await query.message.edit_text(Txt.ASK_SUFFIX)
        client.user_data[user_id]['state'] = States.WAITING_SUFFIX
    
    elif data == "skip_modifiers":
        await process_file_renaming(client, query)
    
    elif data == "process_file":
        await process_file_renaming(client, query)
    
    elif data == "close":
        await query.message.delete()
    
    # Add other callback handlers as needed

async def process_file_renaming(client: Client, query: CallbackQuery):
    """Process the file renaming operation"""
    user_id = query.from_user.id
    user_data = client.user_data.get(user_id, {})
    
    try:
        # Construct final filename
        prefix = user_data.get('prefix', '')
        suffix = user_data.get('suffix', '')
        new_name = user_data['new_name']
        
        final_name = f"{prefix}{new_name}{suffix}"
        
        # Download the file
        download_msg = await query.message.reply_text(Txt.DOWNLOADING)
        file_path = await client.download_media(
            user_data['file_id'],
            file_name=os.path.join("downloads", user_data['temp_name'])
        )
        
        # Rename the file
        new_path = os.path.join("downloads", final_name)
        os.rename(file_path, new_path)
        
        # Upload the renamed file
        await download_msg.edit_text(Txt.UPLOADING)
        
        if user_data['file_type'] == 'document':
            await client.send_document(
                chat_id=user_id,
                document=new_path,
                file_name=final_name,
                caption=Txt.FILE_CAPTION.format(final_name)
            )
        elif user_data['file_type'] == 'video':
            await client.send_video(
                chat_id=user_id,
                video=new_path,
                caption=Txt.FILE_CAPTION.format(final_name)
            )
        elif user_data['file_type'] == 'audio':
            await client.send_audio(
                chat_id=user_id,
                audio=new_path,
                caption=Txt.FILE_CAPTION.format(final_name)
            )
        
        # Clean up
        os.remove(new_path)
        await download_msg.delete()
        await query.message.edit_text(Txt.SUCCESS_MSG)
        
        # Clear user data
        del client.user_data[user_id]
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await query.message.edit_text(Txt.ERROR_PROCESSING)
        if user_id in client.user_data:
            del client.user_data[user_id]

# Helper functions for callback handlers
async def handle_start_callback(query: CallbackQuery):
    await query.message.edit_text(
        text=Txt.START_TXT.format(query.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('• ᴀʙᴏᴜᴛ •', callback_data='about'),
             InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='help')],
            [InlineKeyboardButton("♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻", url=Config.DEVELOPER_URL)]
        ])
    )

async def handle_help_callback(query: CallbackQuery):
    await query.message.edit_text(
        text=Txt.HELP_TXT,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("sᴇᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data="meta")],
            [InlineKeyboardButton("ᴘʀᴇꜰɪx", callback_data="prefix"),
             InlineKeyboardButton("sᴜꜰꜰɪx", callback_data="suffix")],
            [InlineKeyboardButton("ᴄᴀᴘᴛɪᴏɴ", callback_data="caption"),
             InlineKeyboardButton("ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="thumbnail")],
            [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start")]
        ])
    )

async def handle_about_callback(query: CallbackQuery):
    await query.message.edit_text(
        text=Txt.ABOUT_TXT,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻  ʀᴇᴘᴏ", url=Config.REPO_URL),
             InlineKeyboardButton("💥  ᴅᴏɴᴀᴛᴇ", callback_data="donate")],
            [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start")]
        ])
    )