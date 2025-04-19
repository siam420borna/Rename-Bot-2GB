import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from plugins.database import data  # Use absolute import to avoid deployment issues

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Replace ADMIN with your admin ID or get it from a config
ADMIN = [7862181538]  # Replace with your admin user ID(s)

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMIN))
async def broadcast(client: Client, message: Message):
    try:
        msg = await message.reply_text("Wait a second!")
        
        if not message.reply_to_message:
            return await msg.edit("Please reply to a message to broadcast.")
        
        await msg.edit("Processing ...")
        completed, failed = 0, 0
        to_copy_msg = message.reply_to_message
        users_list = await data.get_all_users()
        
        for i, userDoc in enumerate(users_list):
            if i % 20 == 0:
                await msg.edit(f"Broadcasting...\nTotal Processed: {i}\n✅ Completed: {completed}\n❌ Failed: {failed}")
            
            user_id = userDoc.get("user_id")
            if not user_id:
                continue
            
            try:
                await to_copy_msg.copy(int(user_id))
                completed += 1
                await asyncio.sleep(0.1)

            except FloodWait as e:
                logger.warning(f"Flood wait for {e.value} seconds while sending to {user_id}")
                await asyncio.sleep(e.value)
                try:
                    await to_copy_msg.copy(int(user_id))
                    completed += 1
                except Exception as e:
                    logger.error(f"Retry failed for {user_id}: {e}")
                    failed += 1

            except Exception as e:
                logger.error(f"Error broadcasting to {user_id}: {e}")
                failed += 1
        
        await msg.edit(
            f"✅ Successfully Broadcasted!\n\n"
            f"👥 Total Users: {len(users_list)}\n"
            f"✅ Completed: {completed}\n"
            f"❌ Failed: {failed}"
        )
    
    except Exception as e:
        logger.exception("An unexpected error occurred during broadcast.")
        await message.reply_text("An error occurred while broadcasting.")