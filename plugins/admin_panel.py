import os, sys, time, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from helper.database import jishubotz
import asyncio
import time

ADMIN_ID = 123456789  # change this to your Telegram user ID

@Client.on_message(filters.private & filters.command("status"))
async def status_handler(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    total_users = await jishubotz.total_users()
    total_premium = await jishubotz.total_premium_users()
    await message.reply_text(f"👥 Total Users: `{total_users}`\n⭐ Premium Users: `{total_premium}`")


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
    
    users = await jishubotz.get_all_users()
    sent, failed = 0, 0

    for user_id in users:
        try:
            await client.copy_message(user_id, message.chat.id, message.reply_to_message.message_id)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await message.reply_text(f"✅ Broadcast completed!\n\nSent: `{sent}`\nFailed: `{failed}`")


@Client.on_message(filters.private & filters.command("addpremium"))
async def add_premium(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("❗ Usage:\n`/addpremium user_id`")

    user_id = int(message.command[1])
    await jishubotz.add_premium(user_id)
    await message.reply_text(f"✅ Added premium to `{user_id}`")


@Client.on_message(filters.private & filters.command("delpremium"))
async def del_premium(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ You're not authorized to use this command.")
    
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("❗ Usage:\n`/delpremium user_id`")

    user_id = int(message.command[1])
    await jishubotz.remove_premium(user_id)
    await message.reply_text(f"✅ Removed premium from `{user_id}`")