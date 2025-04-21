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








#gpt


import os
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import requests
from io import BytesIO

# Welcome card generator
def generate_welcome_card(name, username, user_id, profile_url=None):
    bg = Image.open("welcome_bg.jpg").convert("RGBA")
    draw = ImageDraw.Draw(bg)

    font_big = ImageFont.truetype("arial.ttf", 60)
    font_small = ImageFont.truetype("arial.ttf", 36)

    # Text draw
    draw.text((50, 50), "WELCOME", font=font_big, fill="white")
    draw.text((50, 150), f"NAME     : {name}", font=font_small, fill="white")
    draw.text((50, 210), f"USERNAME : @{username}" if username else "USERNAME : None", font=font_small, fill="white")
    draw.text((50, 270), f"USER ID  : {user_id}", font=font_small, fill="white")

    # Profile pic
    avatar_size = (200, 200)
    if profile_url:
        response = requests.get(profile_url)
        avatar = Image.open(BytesIO(response.content)).resize(avatar_size)
    else:
        avatar = Image.open("default_avatar.png").resize(avatar_size)

    bg.paste(avatar, (1000, 50))

    output = BytesIO()
    output.name = "welcome.png"
    bg.save(output, "PNG")
    output.seek(0)
    return output

# Main function
def welcome(update: Update, context: CallbackContext):
    for user in update.message.new_chat_members:
        name = user.full_name
        username = user.username or "None"
        user_id = user.id

        # Try to get profile pic URL
        photos = context.bot.get_user_profile_photos(user.id)
        profile_url = None
        if photos.total_count > 0:
            file = context.bot.get_file(photos.photos[0][0].file_id)
            profile_url = file.file_path

        # Generate image
        img = generate_welcome_card(name, username, user_id, profile_url)

        # Send image
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=img,
            caption=f"স্বাগতম @{username}!"
        )

# Setup
updater = Updater("8043487250:AAHi4LvR7TW-1RfRva1SWBacBnbCnHCFwcs", use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))

updater.start_polling()
updater.idle()







# -----------------------------
# Run the Bot
# -----------------------------
Bot().run()