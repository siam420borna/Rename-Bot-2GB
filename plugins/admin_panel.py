import os, sys, time, asyncio, logging, datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

from config import Config, ADMINS
from helper.database import db  # ঠিকভাবে import করলাম

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Status Command
@Client.on_message(filters.command("status") & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))
    start_t = time.time()
    st = await message.reply('**Processing The Details.....**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bot Stats--** \n\n**⌚ Bot Uptime:** `{uptime}` \n**🐌 Current Ping:** `{time_taken_s:.3f} ms` \n**👭 Total Users:** `{total_users}`")

# Restart Command
@Client.on_message(filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(bot, message):
    msg = await bot.send_message(text="🔄 Processes Stopped. Bot Is Restarting...", chat_id=message.chat.id)
    await asyncio.sleep(3)
    await msg.edit("✅️ Bot Is Restarted. Now You Can Use Me")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Ping Command
@Client.on_message(filters.private & filters.command("ping"))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("Pinging....")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Ping 🔥!\n{time_taken_s:.3f} ms")
    return time_taken_s

# Broadcast
@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    try:
        await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} started a broadcast.")
    except Exception as e:
        print("Log channel error:", e)

    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Broadcast Started..!")

    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()

    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user['_id'])
        done += 1
        if done % 20 == 0:
            try:
                await sts_msg.edit(f"**Broadcast In Progress:** \n\nTotal Users: {total_users} \nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}")
            except Exception as e:
                logger.warning(f"Edit failed: {e}")

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"**Broadcast Completed:** \n\nCompleted In `{completed_in}`.\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}")

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
        logger.error(f"{user_id} : {e}")
        return 500

# Premium Management
@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def cmd_add_premium(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Usage: /addpremium user_id")
    user_id = int(m.command[1])
    await db.add_premium(user_id)
    await m.reply(f"✅ User {user_id} added as Premium.")

@Client.on_message(filters.command("delpremium") & filters.user(ADMINS))
async def cmd_del_premium(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Usage: /delpremium user_id")
    user_id = int(m.command[1])
    await db.remove_premium(user_id)
    await m.reply(f"❌ User {user_id} removed from Premium.")

@Client.on_message(filters.command("ispremium"))
async def check_premium(_, m: Message):
    is_prem = await db.is_premium(m.from_user.id)
    if is_prem:
        await m.reply("✅ You are a Premium user.")
    else:
        await m.reply("❌ You are not a Premium user.")

@Client.on_message(filters.command("togglepremium") & filters.user(ADMINS))
async def toggle_premium_mode(client, message: Message):
    current = await db.is_premium_enabled()
    await db.set_premium_enabled(not current)
    if not current:
        await message.reply("✅ প্রিমিয়াম মোড **চালু** করা হয়েছে। এখন শুধু প্রিমিয়াম ইউজাররা বিশেষ ফিচার ব্যবহার করতে পারবে।")
    else:
        await message.reply("⚠️ প্রিমিয়াম মোড **বন্ধ** করা হয়েছে। এখন সবাই সব ফিচার ব্যবহার করতে পারবে।")