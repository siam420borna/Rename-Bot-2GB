import os, sys, time, asyncio, logging, datetime, shutil
from config import Config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from helper.database import jishubotz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_readable_time(seconds: int) -> str:
    periods = [
        ('day', 86400),
        ('hour', 3600),
        ('minute', 60),
        ('second', 1)
    ]
    parts = []
    for name, count in periods:
        value = seconds // count
        if value:
            seconds -= value * count
            parts.append(f"{value} {name}{'s' if value > 1 else ''}")
    return ', '.join(parts)

@Client.on_message(filters.command("status") & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await jishubotz.total_users_count()
    uptime = get_readable_time(int(time.time() - bot.uptime))
    start_time = time.time()

    # Active users in last 7 days
    active_users = await jishubotz.count_active_users(days=7)

    msg = await message.reply("⚡ Processing bot stats...")
    end_time = time.time()
    ping = (end_time - start_time) * 1000

    # Storage info (if running on disk)
    total, used, free = shutil.disk_usage(".")
    used_gb = used // (2**30)
    total_gb = total // (2**30)

    await msg.edit(
        f"**🤖 Bot Status:**\n\n"
        f"**⏱ Uptime:** `{uptime}`\n"
        f"**📶 Ping:** `{ping:.2f} ms`\n"
        f"**👥 Total Users:** `{total_users}`\n"
        f"**✅ Active (7d):** `{active_users}`\n"
        f"**💾 Disk Usage:** `{used_gb} GB / {total_gb} GB`\n",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Restart", callback_data="admin_restart")],
            [InlineKeyboardButton("🔙 Close", callback_data="admin_close")]
        ])
    )

@Client.on_message(filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(bot, message):
    msg = await message.reply("♻️ Restarting bot...")
    await asyncio.sleep(3)
    await msg.edit("✅ Restart complete.")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("ping") & filters.user(Config.ADMIN))
async def ping(_, message):
    start = time.time()
    m = await message.reply("🏓 Pinging...")
    end = time.time()
    await m.edit(f"**Pong:** `{(end-start)*1000:.2f} ms`")

@Client.on_message(filters.command("userinfo") & filters.user(Config.ADMIN))
async def userinfo(bot, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/userinfo user_id`")
    user_id = int(message.command[1])
    try:
        user = await bot.get_users(user_id)
        mention = user.mention
        is_registered = await jishubotz.is_user_exist(user_id)
        await message.reply(
            f"**👤 User Info:**\n\n"
            f"**ID:** `{user.id}`\n"
            f"**Name:** {user.first_name}\n"
            f"**Username:** @{user.username if user.username else 'N/A'}\n"
            f"**Mention:** {mention}\n"
            f"**Registered:** {'✅ Yes' if is_registered else '❌ No'}"
        )
    except Exception as e:
        await message.reply(f"⚠️ Failed to get user info:\n`{e}`")

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    try:
        await bot.send_message(Config.LOG_CHANNEL, f"📢 Broadcast initiated by {m.from_user.mention} (`{m.from_user.id}`)")
    except Exception as e:
        logger.warning("Log channel issue: %s", e)

    users = await jishubotz.get_all_users()
    msg = m.reply_to_message
    done, success, failed = 0, 0, 0
    sts = await m.reply("🚀 Broadcast started...")
    total = await jishubotz.total_users_count()
    start_time = time.time()

    async for u in users:
        status = await send_msg(u['_id'], msg)
        if status == 200:
            success += 1
        else:
            failed += 1
            if status == 400:
                await jishubotz.delete_user(u['_id'])
        done += 1
        if done % 20 == 0:
            try:
                await sts.edit(f"**Broadcast In Progress:**\n✅ Success: {success}\n❌ Failed: {failed}\n📤 Done: {done}/{total}")
            except:
                pass

    duration = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(f"✅ **Broadcast Complete:**\n\n⏱ Duration: `{duration}`\n📊 Success: `{success}`\n⚠ Failed: `{failed}`\n👥 Total: `{total}`")

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
        logger.error(f"[{user_id}] Broadcast error: {e}")
        return 500

@Client.on_callback_query(filters.regex("admin_"))
async def admin_callback(bot, query):
    data = query.data
    if data == "admin_restart":
        await query.message.edit("♻️ Restarting bot...")
        await asyncio.sleep(3)
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif data == "admin_close":
        try:
            await query.message.delete()
        except:
            pass