from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from helper.database import db

@Client.on_message(filters.private & filters.video)
async def check_token_or_premium(client, message: Message):
    user_id = message.from_user.id

    # যদি ইউজার প্রিমিয়াম হয়, তাহলে ছাড়
    if await db.is_premium(user_id):
        return

    # যদি টোকেন ভেরিফায়েড থাকে, তাহলে ছাড়
    if await db.get_verified_token(user_id):
        return

    # না হলে ভেরিফিকেশন মেসেজ পাঠাও এবং পরবর্তী হ্যান্ডলার ব্লক করো
    await message.reply_text(
        "**⚠️ প্রথমে টোকেন ভেরিফাই করতে হবে!**\n\nভেরিফাই না করলে ফাইল রিনেম হবে না।",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ টোকেন ভেরিফাই করুন", url=f"https://tnlink.in/your_link_here?user_id={user_id}")]]
        )
    )