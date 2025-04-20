import os, sys, time, asyncio, logging, datetime
from config import Config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from helper.database import jishubotz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Admin Panel Command
@Client.on_message(filters.command("admin") & filters.user(Config.ADMIN))
async def admin_panel(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 অবস্থা", callback_data="status"),
         InlineKeyboardButton("♻️ রিস্টার্ট", callback_data="restart")],
        [InlineKeyboardButton("📣 সম্প্রচার", callback_data="broadcast")],
        [InlineKeyboardButton("❌ বন্ধ করুন", callback_data="close")]
    ])
    await message.reply("**🔐 অ্যাডমিন কন্ট্রোল প্যানেল**", reply_markup=keyboard)

# Callback Handlers
@Client.on_callback_query(filters.user(Config.ADMIN))
async def admin_callbacks(client, query: CallbackQuery):
    data = query.data
    if data == "status":
        total_users = await jishubotz.total_users_count()
        uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))
        start_time = time.time()
        await query.message.edit("⏳ অনুরোধ প্রক্রিয়াকরণ হচ্ছে...")
        ping = (time.time() - start_time) * 1000
        await query.message.edit_text(
            f"**✅ বট স্ট্যাটাস**\n\n"
            f"⌚ আপটাইম: `{uptime}`\n"
            f"📡 পিং: `{ping:.3f} ms`\n"
            f"👥 মোট ব্যবহারকারী: `{total_users}`"
        )

    elif data == "restart":
        await query.message.edit("♻️ রিস্টার্ট হচ্ছে...")
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "broadcast":
        await query.message.edit("**ℹ️ সম্প্রচার করতে একটি মেসেজে রিপ্লাই করে `/broadcast` লিখুন।**")

    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass

# /status command
@Client.on_message(filters.command("status") & filters.user(Config.ADMIN))
async def bot_status(client, message):
    total_users = await jishubotz.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))
    start_time = time.time()
    status_msg = await message.reply("**⏳ বিস্তারিত নেওয়া হচ্ছে...**")
    ping = (time.time() - start_time) * 1000
    await status_msg.edit(
        f"**--বট স্ট্যাটাস--** \n\n"
        f"⌚ আপটাইম: `{uptime}`\n"
        f"📡 পিং: `{ping:.3f} ms`\n"
        f"👥 মোট ব্যবহারকারী: `{total_users}`"
    )

# /restart command
@Client.on_message(filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(client, message):
    msg = await message.reply("♻️ রিস্টার্ট হচ্ছে...")
    await asyncio.sleep(2)
    os.execl(sys.executable, sys.executable, *sys.argv)

# /ping command
@Client.on_message(filters.command("ping") & filters.user(Config.ADMIN))
async def bot_ping(client, message):
    start_time = time.time()
    msg = await message.reply("পিং হচ্ছে...")
    ping = (time.time() - start_time) * 1000
    await msg.edit(f"🔥 পিং: `{ping:.3f} ms`")

# /broadcast command
@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(client: Client, message: Message):
    try:
        await client.send_message(Config.LOG_CHANNEL, f"{message.from_user.mention} সম্প্রচার শুরু করেছেন।")
    except Exception as e:
        logger.error(f"Log channel error: {e}")

    all_users = await jishubotz.get_all_users()
    broadcast_msg = message.reply_to_message
    status_msg = await message.reply_text("📣 সম্প্রচার শুরু হয়েছে...")

    total = await jishubotz.total_users_count()
    done, failed, success = 0, 0, 0
    start_time = time.time()

    async for user in all_users:
        result = await send_broadcast(user['_id'], broadcast_msg)
        if result == 200:
            success += 1
        elif result == 400:
            await jishubotz.delete_user(user['_id'])
            failed += 1
        else:
            failed += 1
        done += 1

        if done % 20 == 0:
            try:
                await status_msg.edit(
                    f"📤 সম্প্রচার চলছে:\n"
                    f"মোট: {total}\nসম্পন্ন: {done}/{total}\n✅ সফল: {success}\n❌ ব্যর্থ: {failed}"
                )
            except Exception:
                pass

    duration = str(datetime.timedelta(seconds=int(time.time() - start_time)))
    await status_msg.edit(
        f"✅ **সম্প্রচার শেষ!**\n\nসময় লেগেছে: `{duration}`\n"
        f"মোট: {total}\n✅ সফল: {success}\n❌ ব্যর্থ: {failed}"
    )

# Broadcast message function
async def send_broadcast(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_broadcast(user_id, message)
    except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
        return 400
    except Exception as e:
        logger.error(f"Broadcast error to {user_id}: {e}")
        return 500