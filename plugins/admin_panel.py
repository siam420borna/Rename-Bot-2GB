import os, sys, time, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from helper.database import db  # ei line correct

ADMIN_ID = 123456789  # eta nijer Telegram ID diye replace kor

@Client.on_message(filters.private & filters.command("status"))
async def status_handler(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    total_users = await db.total_users_count()
    premium_users = await db.user_col.count_documents({"premium": True})
    
    await message.reply_text(
        f"👥 Total Users: `{total_users}`\n"
        f"⭐ Premium Users: `{premium_users}`"
    )


@Client.on_message(filters.private & filters.command("restart"))
async def restart_handler(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    await message.reply_text("♻️ Restarting...")
    await asyncio.sleep(2)
    exit(0)


@Client.on_message(filters.private & filters.command("broadcast"))
async def broadcast_handler(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    if not message.reply_to_message:
        return await message.reply("❗ Reply to a message to broadcast it.")
    
    sent = failed = 0
    async for user in db.get_all_users():
        try:
            await client.copy_message(
                chat_id=user['_id'],
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await message.reply_text(f"✅ Broadcast finished!\n\nSent: `{sent}`\nFailed: `{failed}`")


@Client.on_message(filters.private & filters.command("addpremium"))
async def add_premium_handler(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("❗ Usage:\n`/addpremium user_id`")
    
    user_id = int(message.command[1])
    await db.add_premium(user_id)
    await message.reply_text(f"✅ Premium access given to `{user_id}`")


@Client.on_message(filters.private & filters.command("delpremium"))
async def remove_premium_handler(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("❗ Usage:\n`/delpremium user_id`")
    
    user_id = int(message.command[1])
    await db.remove_premium(user_id)
    await message.reply_text(f"✅ Premium removed from `{user_id}`")