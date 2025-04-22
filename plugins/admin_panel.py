import os, sys, time, asyncio, datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

from config import Config, ADMINS
from helper.database import db

# Status
@Client.on_message(filters.command("status") & filters.user(Config.ADMIN))
async def status(bot, msg):
    total = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))
    st = await msg.reply("Checking...")
    ping = (time.time() - st.date.timestamp()) * 1000
    await st.edit(f"**Bot Uptime:** `{uptime}`\n**Ping:** `{ping:.3f} ms`\n**Users:** `{total}`")

# Restart
@Client.on_message(filters.command("restart") & filters.user(Config.ADMIN))
async def restart(_, msg):
    await msg.reply("♻️ Restarting...")
    await asyncio.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)

# Ping
@Client.on_message(filters.command("ping"))
async def ping(_, msg):
    start = time.time()
    m = await msg.reply("Pinging...")
    await m.edit(f"Pong: `{(time.time() - start)*1000:.2f} ms`")

# Broadcast
@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast(bot, msg):
    users = db.get_all_users()
    done, fail = 0, 0
    start = time.time()
    stat = await msg.reply("Broadcasting...")

    async for u in users:
        try:
            await msg.reply_to_message.copy(u['_id'])
            done += 1
        except (FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
            await db.delete_user(u['_id'])
            fail += 1
        if done % 20 == 0:
            await stat.edit(f"✅ Done: {done} | ❌ Failed: {fail}")

    t = str(datetime.timedelta(seconds=int(time.time() - start)))
    await stat.edit(f"✅ Done: {done}\n❌ Failed: {fail}\n⏱ Time: {t}")

# Premium Commands
@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium(_, m):
    if len(m.command) < 2: return await m.reply("Usage: /addpremium user_id")
    await db.add_premium(int(m.command[1]))
    await m.reply("✅ Added as Premium.")

@Client.on_message(filters.command("delpremium") & filters.user(ADMINS))
async def del_premium(_, m):
    if len(m.command) < 2: return await m.reply("Usage: /delpremium user_id")
    await db.remove_premium(int(m.command[1]))
    await m.reply("❌ Removed from Premium.")

@Client.on_message(filters.command("ispremium"))
async def check_premium(_, m):
    prem = await db.is_premium(m.from_user.id)
    await m.reply("✅ Premium." if prem else "❌ Not Premium.")

@Client.on_message(filters.command("togglepremium") & filters.user(ADMINS))
async def toggle_premium(_, m):
    status = await db.is_premium_enabled()
    await db.set_premium_enabled(not status)
    msg = "✅ প্রিমিয়াম মোড **চালু** করা হয়েছে।" if not status else "❌ প্রিমিয়াম মোড **বন্ধ** করা হয়েছে।"
    await m.reply(msg)