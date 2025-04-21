import os, sys, time, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
from helper.database import jishubotz

@Client.on_message(filters.command("admin") & filters.user(Config.ADMIN))
async def admin_panel(_, m: Message):
    buttons = [
        [
            InlineKeyboardButton("📊 স্ট্যাটাস", callback_data="status"),
            InlineKeyboardButton("🔁 রিস্টার্ট", callback_data="restart"),
        ],
        [
            InlineKeyboardButton("📣 ব্রডকাস্ট", callback_data="broadcast"),
            InlineKeyboardButton("🏆 প্রিমিয়াম", callback_data="premium_menu"),
        ],
    ]
    await m.reply("অ্যাডমিন কন্ট্রোল প্যানেল", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.user(Config.ADMIN))
async def admin_cb_handler(_, query: CallbackQuery):
    data = query.data

    if data == "status":
        total_users = await jishubotz.total_users_count()
        uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - _.uptime))
        await query.message.edit(
            f"**--বট স্ট্যাটাস--**\n\n⌚ **আপটাইম:** `{uptime}`\n👥 **মোট ইউজার:** `{total_users}`"
        )

    elif data == "restart":
        await query.message.edit("♻️ বট রিস্টার্ট হচ্ছে...")
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "broadcast":
        await query.message.edit("✉️ যে মেসেজটা পাঠাতে চাও, সেটার রিপ্লাই দাও এই মেসেজটার উপরে।")

    elif data == "premium_menu":
        buttons = [
            [
                InlineKeyboardButton("➕ অ্যাড প্রিমিয়াম", callback_data="add_premium"),
                InlineKeyboardButton("➖ রিমুভ প্রিমিয়াম", callback_data="del_premium"),
            ]
        ]
        await query.message.edit("**প্রিমিয়াম ইউজার কন্ট্রোল**", reply_markup=InlineKeyboardMarkup(buttons))

    await query.answer()

@Client.on_callback_query(filters.regex("add_premium") & filters.user(Config.ADMIN))
async def ask_add_premium(_, query: CallbackQuery):
    await query.message.edit("➕ ইউজার আইডি দিন প্রিমিয়াম অ্যাড করার জন্য। /addpremium user_id")

@Client.on_callback_query(filters.regex("del_premium") & filters.user(Config.ADMIN))
async def ask_del_premium(_, query: CallbackQuery):
    await query.message.edit("➖ ইউজার আইডি দিন প্রিমিয়াম রিমুভ করার জন্য। /delpremium user_id")