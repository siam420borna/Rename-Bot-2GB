from pyrogram import filters
from pyrogram.types import Message
from main import app
from helper.shortlink import create_shortlink
from helper.database import is_verified, set_verified

@app.on_message(filters.video & filters.private)
async def verify_token_before_process(client, message: Message):
    user_id = message.from_user.id

    if not await is_verified(user_id):
        short_url = await create_shortlink(user_id)
        if not short_url:
            return await message.reply("ভেরিফিকেশন লিংক তৈরি করতে সমস্যা হয়েছে। পরে আবার চেষ্টা করুন।")

        return await message.reply(
            f"আপনার ভিডিও প্রসেস করার আগে টোকেন ভেরিফিকেশন প্রয়োজন।\n\nঅনুগ্রহ করে নিচের লিংকে ক্লিক করুন:\n\n{short_url}"
        )

    await message.reply("আপনার ভিডিও এখন প্রসেস হচ্ছে...")