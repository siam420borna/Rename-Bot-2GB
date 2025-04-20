from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import Config
from helper.database import jishubotz
import time, os, asyncio

ADMIN_ID = Config.OWNER_ID

@Client.on_message(filters.private & filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(client: Client, message: Message):
    total_users = await jishubotz.total_users_count()
    await message.reply_text(
        f"**👑 অ্যাডমিন প্যানেল**\n\n"
        f"• মোট ইউজার: `{total_users}` জন\n"
        f"• বট স্ট্যাটাস: ✅ অনলাইন\n\n"
        f"নীচের বাটন থেকে টুলস বেছে নিন:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 ইউজার সংখ্যা", callback_data="users"),
             InlineKeyboardButton("📶 পিং", callback_data="ping")],
            [InlineKeyboardButton("♻️ রিস্টার্ট", callback_data="restart")],
            [InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="broadcast")],
            [InlineKeyboardButton("⛔ ব্যান", callback_data="ban_user"),
             InlineKeyboardButton("✅ আনব্যান", callback_data="unban_user")],
        ])
    )


# Callback Functions
@Client.on_callback_query(filters.regex("users") & filters.user(ADMIN_ID))
async def total_users_cb(client, callback_query: CallbackQuery):
    total = await jishubotz.total_users_count()
    await callback_query.answer(f"মোট ইউজার: {total}", show_alert=True)

@Client.on_callback_query(filters.regex("ping") & filters.user(ADMIN_ID))
async def ping_cb(client, callback_query: CallbackQuery):
    start = time.time()
    msg = await callback_query.message.reply("পিং হচ্ছে...")
    end = time.time()
    await msg.edit(f"🏓 পং! `{round((end-start)*1000)}ms`")

@Client.on_callback_query(filters.regex("restart") & filters.user(ADMIN_ID))
async def restart_cb(client, callback_query: CallbackQuery):
    await callback_query.message.edit("♻️ রিস্টার্ট হচ্ছে, একটু অপেক্ষা করুন...")
    await asyncio.sleep(2)
    os.execl(sys.executable, sys.executable, *sys.argv)


# Broadcast handler (manual command based)
@Client.on_message(filters.private & filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_msg(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("ব্যবহার:\n`/broadcast আপনার_মেসেজ`")
    
    text = message.text.split(None, 1)[1]
    total = 0
    failed = 0

    async for user in jishubotz.get_all_users():
        try:
            await client.send_message(user['_id'], text)
            total += 1
        except:
            failed += 1
    
    await message.reply(f"✅ পাঠানো হয়েছে: {total}\n❌ ব্যর্থ হয়েছে: {failed}")


# Ban/unban command based
@Client.on_message(filters.private & filters.command("ban") & filters.user(ADMIN_ID))
async def ban_user_cmd(client, message: Message):
    if len(message.command) != 2:
        return await message.reply("ব্যবহার:\n`/ban ইউজার_আইডি`")
    user_id = int(message.command[1])
    done = await jishubotz.ban_user(user_id)
    if done:
        await message.reply(f"⛔ `{user_id}` ব্যান করা হয়েছে।")
    else:
        await message.reply("ইউজার ইতোমধ্যে ব্যানড।")

@Client.on_message(filters.private & filters.command("unban") & filters.user(ADMIN_ID))
async def unban_user_cmd(client, message: Message):
    if len(message.command) != 2:
        return await message.reply("ব্যবহার:\n`/unban ইউজার_আইডি`")
    user_id = int(message.command[1])
    done = await jishubotz.is_unbanned(user_id)
    if done:
        await message.reply(f"✅ `{user_id}` আনব্যান করা হয়েছে।")
    else:
        await message.reply("ইউজার ব্যানড ছিল না।")