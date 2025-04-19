import os
from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from route import web_server
import pyrogram.utils
import pyromod
from pyrogram import filters
from pyrogram.types import Message


from pyrogram import Client, filters

# ================================
# Forward all private incoming msgs
# ================================
@Client.on_message(filters.private & filters.incoming)
async def forward_to_log(client: Client, message: Message):
    try:
        await message.forward(chat_id=Config.LOG_CHANNEL)
    except Exception as e:
        print(f"[FORWARD ERROR] {e}")


from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# ================================
# Forward all private incoming msgs
# ================================
@Client.on_message(filters.private & filters.incoming)
async def forward_to_log(client: Client, message: Message):
    try:
        await message.forward(chat_id=Config.LOG_CHANNEL)
    except Exception as e:
        print(f"[FORWARD ERROR] {e}")








# -----------------------------
# Logging All Private Messages
# -----------------------------
@Client.on_message(filters.private & ~filters.command(["start", "help", "ping", "status", "broadcast", "ban", "unban"]))
async def log_all_private_messages(bot, message: Message):
    try:
        user = message.from_user
        text = message.text or "No Text"
        await bot.send_message(
            chat_id=Config.LOG_CHANNEL,
            text=f"**#NEW_MESSAGE_LOGGED**\n\n**From:** `{user.id}` - {user.first_name}\n**Username:** @{user.username if user.username else 'N/A'}\n\n**Message:**\n{text}"
        )
    except Exception as e:
        print(f"[LOGGING ERROR] => {e}")

# -----------------------------
# Pyrogram Minimum ID Fix
# -----------------------------
pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

# -----------------------------
# Bot Class
# -----------------------------
class Bot(Client):

    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME     

        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()
            PORT = int(os.environ.get("PORT", 8000))  # Default port is 8000
            await web.TCPSite(app, "0.0.0.0", PORT).start()

        print(f"{me.first_name} Is Started.....✨️")

        for id in Config.ADMIN:
            try: 
                await self.send_message(id, f"**{me.first_name} Is Started...**")                                
            except Exception as e:
                print(f"Error sending message to admin {id}: {e}")
        
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`"
                )                                
            except Exception as e:
                print(f"Error sending message to LOG_CHANNEL: {e}")

    async def stop(self):
        await super().stop()
        print(f"{self.mention} is stopped.")

# -----------------------------
# Run the Bot
# -----------------------------
Bot().run()