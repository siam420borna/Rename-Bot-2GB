from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from helper.database import jishubotz, set_watermark, get_watermark, del_watermark
from config import Config

class Txt:
    START_TXT = """
🌟 **Welcome, {0}!** 🌟

✨ **Siam's Renamer Bot** is here to make your files shine! ✨  
Here’s what you can do:  
✅ **Rename** & **edit** files with ease  
✅ Convert **video to file** or **file to video**  
✅ Add custom **thumbnails**, **captions**, **prefixes**, & **suffixes**

⚠️ **Important**: Adult content is strictly **prohibited**. Violators will be **banned permanently**!

👉 Press the buttons below to explore more! 🚀
"""

    HELP_TXT = """
🛠 **How to Use Siam's Renamer Bot** 🛠

1️⃣ **Send a file** you want to rename  
2️⃣ Reply with the **new name** when prompted  
3️⃣ Receive your **renamed file** with updated metadata  

🎯 **Features**:  
• `/set_caption` - Add a custom caption  
• `/set_prefix` or `/set_suffix` - Customize filenames  
• `/set_watermark` - Add text watermark to video thumbnails  
• `/del_watermark` - Remove watermark  

📚 Explore more with the buttons below! 👇
"""

    ABOUT_TXT = """
ℹ️ **About Siam's Renamer Bot** ℹ️

• **Name**: Siam’s Renamer Bot  
• **Language**: Python 3  
• **Library**: Pyrogram  
• **Hosted On**: Railway  
• **Creator**: Siam (The Boss) 😎  

💡 This bot is **free** and **open-source**, built for your convenience!  

👉 Check out the repo or support the creator below! 🚀
"""

    DONATE_TXT = """
💖 **Support the Creator** 💖  

Love using this bot? Help keep it running!  

💸 **Donate via**:  
• **UPI**: siam@ybl  
• **PayPal**: Coming soon!  

🙌 Even a small contribution means a lot!  

👇 Check out more or return to the menu! 🚪
"""

    SEND_METADATA = """
📝 **Manage Metadata for Your Media** 📝  

Enhance your files with custom metadata!  

🔹 **Available Metadata**:  
• **Title**: Set a descriptive title  
• **Author**: Define the creator  
• **Artist**: Specify the artist  
• **Audio**: Add audio title  
• **Subtitle**: Set subtitle title  
• **Video**: Define video title  

🔧 **Commands**:  
• `/metadata` - Enable/disable metadata  
• `/settitle` - Set custom title (e.g., `/settitle My Video`)  
• `/setauthor` - Set author  
• `/setartist` - Set artist  
• `/setaudio` - Set audio title  
• `/setsubtitle` - Set subtitle title  
• `/setvideo` - Set video title  

💡 **Example**: `/settitle Awesome Movie`  

🚀 Use these to make your media stand out!  
"""

    PREFIX = """
✍️ **Set a Custom Prefix** ✍️  

Add a prefix to your filenames for better organization!  

🔹 **Commands**:  
• `/set_prefix` - Set a custom prefix (e.g., `/set_prefix [Siam Bot]`)  
• `/del_prefix` - Remove the prefix  
• `/see_prefix` - View your current prefix  

💡 **Example**: `/set_prefix [Siam Bot]`  

👉 Try it now! 🚀
"""

    SUFFIX = """
✍️ **Set a Custom Suffix** ✍️  

Add a suffix to your filenames for a unique touch!  

🔹 **Commands**:  
• `/set_suffix` - Set a custom suffix (e.g., `/set_suffix [Siam Maker]`)  
• `/del_suffix` - Remove the suffix  
• `/see_suffix` - View your current suffix  

💡 **Example**: `/set_suffix [Siam Maker]`  

👉 Get started! 🚀
"""

    CAPTION_TXT = """
🖋 **Set a Custom Caption** 🖋  

Personalize your file captions with dynamic variables!  

🔹 **Variables**:  
• `{filename}` - File name  
• `{filesize}` - File size  
• `{duration}` - Media duration  

🔹 **Commands**:  
• `/set_caption` - Set a custom caption (e.g., `/setcaption File: {filename}`)  
• `/see_caption` - View your current caption  
• `/del_caption` - Remove the caption  

💡 **Example**: `/setcaption File: {filename} | Size: {filesize}`  

👉 Customize now! 🚀
"""

    THUMBNAIL_TXT = """
🖼 **Set a Custom Thumbnail** 🖼  

Make your files visually appealing with a custom thumbnail!  

🔹 **How to Set**:  
• Send any **photo** to automatically set it as a thumbnail  
• `/del_thumb` - Delete your current thumbnail  
• `/view_thumb` - View your current thumbnail  

📌 **Note**: If no thumbnail is set, the bot uses the file’s original thumbnail.  

👉 Upload a photo to start! 🚀
"""

    WATERMARK_TXT = """
✒️ **Add a Watermark to Thumbnails** ✒️  

Protect your content with a custom text watermark!  

🔹 **Commands**:  
• `/set_watermark YourText` - Set watermark text (e.g., `/set_watermark My Channel`)  
• `/set_watermark_textsize 36` - Set font size (10-100)  
• `/preview_watermark` - Preview watermark on a blank thumbnail  
• `/del_watermark` - Remove watermark and reset font size  

📌 **Note**: Watermarks are automatically applied to all future thumbnails (with logo).  

💡 **Example**: `/set_watermark My Channel`  

👉 Try it out! 🚀
"""

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    data = message.command[1]
    if data.split("-", 1)[0] == "verify": # set if or elif it depend on your code
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )



    user = message.from_user
    await jishubotz.add_user(client, message)

    keyboard = InlineKeyboardMarkup([  
        [InlineKeyboardButton("📚 About", callback_data="about"),  
         InlineKeyboardButton("🛠 Help", callback_data="help")],  
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/movie_channel8")]  
    ])  

    try:  
        if Config.START_PIC:  
            await message.reply_photo(  
                photo=Config.START_PIC,  
                caption=Txt.START_TXT.format(user.mention),  
                reply_markup=keyboard  
            )  
        else:  
            await message.reply_text(  
                text=Txt.START_TXT.format(user.mention),  
                reply_markup=keyboard,  
                disable_web_page_preview=True  
            )  
    except Exception as e:  
        await message.reply_text(f"⚠️ Error in /start:\n`{e}`")

@Client.on_callback_query()
async def callback(client, query: CallbackQuery):
    data = query.data
    user = query.from_user

    if data == "start":  
        await query.message.edit_text(  
            text=Txt.START_TXT.format(user.mention),  
            disable_web_page_preview=True,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("📚 About", callback_data="about"),  
                 InlineKeyboardButton("🛠 Help", callback_data="help")],  
                [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/movie_channel8")]  
            ])  
        )  

    elif data == "help":  
        await query.message.edit_text(  
            text=Txt.HELP_TXT,  
            disable_web_page_preview=True,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("📝 Metadata", callback_data="meta")],  
                [InlineKeyboardButton("📌 Prefix", callback_data="prefix"),  
                 InlineKeyboardButton("📍 Suffix", callback_data="suffix")],  
                [InlineKeyboardButton("🖋 Caption", callback_data="caption"),  
                 InlineKeyboardButton("🖼 Thumbnail", callback_data="thumbnail")],  
                [InlineKeyboardButton("✒️ Watermark", callback_data="watermark")],  
                [InlineKeyboardButton("🏠 Home", callback_data="start")]  
            ])  
        )  

    elif data == "about":  
        await query.message.edit_text(  
            text=Txt.ABOUT_TXT,  
            disable_web_page_preview=True,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔗 Repo", url="https://github.com/&"),  
                 InlineKeyboardButton("💸 Donate", callback_data="donate")],  
                [InlineKeyboardButton("🏠 Home", callback_data="start")]  
            ])  
        )  

    elif data == "donate":  
        await query.message.edit_text(  
            text=Txt.DONATE_TXT,  
            disable_web_page_preview=True,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🤖 More Bots", url="https://t.me/movie_channel8/8")],  
                [InlineKeyboardButton("🔙 Back", callback_data="about"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "meta":  
        await query.message.edit_text(  
            text=Txt.SEND_METADATA,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔙 Back", callback_data="help"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "prefix":  
        await query.message.edit_text(  
            text=Txt.PREFIX,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔙 Back", callback_data="help"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "suffix":  
        await query.message.edit_text(  
            text=Txt.SUFFIX,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔙 Back", callback_data="help"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "caption":  
        await query.message.edit_text(  
            text=Txt.CAPTION_TXT,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔙 Back", callback_data="help"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "thumbnail":  
        await query.message.edit_text(  
            text=Txt.THUMBNAIL_TXT,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔙 Back", callback_data="help"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "watermark":  
        await query.message.edit_text(  
            text=Txt.WATERMARK_TXT,  
            reply_markup=InlineKeyboardMarkup([  
                [InlineKeyboardButton("🔙 Back", callback_data="help"),  
                 InlineKeyboardButton("❌ Close", callback_data="close")]  
            ])  
        )  

    elif data == "close":  
        try:  
            await query.message.delete()  
        except:  
            pass

@Client.on_message(filters.private & filters.command("set_watermark"))
async def save_watermark(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage**: `/set_watermark YourTextHere`")
    text = message.text.split(None, 1)[1]
    await set_watermark(message.from_user.id, text)
    await message.reply_text(f"✅ **Watermark set to**: `{text}`")

@Client.on_message(filters.private & filters.command("del_watermark"))
async def remove_watermark(client, message: Message):
    await del_watermark(message.from_user.id)
    await message.reply_text("🗑️ **Watermark removed successfully**.")