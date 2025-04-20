import os, sys, time, asyncio, logging, datetime
from config import Config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from helper.database import jishubotz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.command("admin") & filters.user(Config.ADMIN))
async def admin_panel(bot, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 অবস্থা", callback_data="status"),
         InlineKeyboardButton("♻️ রিস্টার্ট", callback_data="restart")],
        [InlineKeyboardButton("📣 সম্প্রচার", callback_data="broadcast")],
        [InlineKeyboardButton("❌ বন্ধ করুন", callback_data="close")]
    ])
    await message.reply("**🔐 অ্যাডমিন কন্ট্রোল প্যানেল**", reply_markup=keyboard)


@Client.on_callback_query(filters.user(Config.ADMIN))
async def admin_callbacks(bot, query: CallbackQuery):
    data = query.data
    if data == "status":
        total_users = await jishubotz.total_users_count()
        uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))
        start_t = time.time()
        await query.message.edit("⏳ অনুরোধ প্রক্রিয়াকরণ হচ্ছে...")
        end_t = time.time()
        ping_time = (end_t - start_t) * 1000
        await query.message.edit_text(
            f"**✅ বট স্ট্যাটাস**\n\n"
            f"⌚ আপটাইম: `{uptime}`\n"
            f"📡 পিং: `{ping_time:.3f} ms`\n"
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


@Client.on_message(filters.command("status") & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await jishubotz.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))
    start_t = time.time()
    st = await message.reply('**⏳ বিস্তারিত নেওয়া হচ্ছে...**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(f"**--বট স্ট্যাটাস--** \n\n**⌚ আপটাইম:** `{uptime}` \n**📡 পিং:** `{time_taken_s:.3f} ms`\n**👥 মোট ব্যবহারকারী:** `{total_users}`")

@Client.on_message(filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(bot, message):
    msg = await message.reply("♻️ রিস্টার্ট হচ্ছে...")
    await asyncio.sleep(2)
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("ping") & filters.user(Config.ADMIN))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("পিং হচ্ছে...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"🔥 পিং: `{time_taken_s:.3f} ms`")

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    try:
        await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} সম্প্রচার শুরু করেছেন।")
    except Exception as e:
        print("LOG_CHANNEL error:", e)

    all_users = await jishubotz.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("📣 সম্প্রচার শুরু হয়েছে...")

    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await jishubotz.total_users_count()

    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await jishubotz.delete_user(user['_id'])
        done += 1
        if done % 20 == 0:
            try:
                await sts_msg.edit(f"**📤 সম্প্রচার চলছে:**\n\nমোট ইউজার: {total_users}\nসম্পন্ন হয়েছে: {done}/{total_users}\nসফল: {success}\nব্যর্থ: {failed}")
            except:
                pass

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"✅ **সম্প্রচার শেষ!**\n\nসময় লেগেছে: `{completed_in}`\nমোট ইউজার: {total_users}\nসফল: {success}\nব্যর্থ: {failed}")

async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
        return 400
    except Exception as e:
        logger.error(f"{user_id}: {e}")
        return 500