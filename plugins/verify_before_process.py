from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from helper.database import db

@Client.on_message(filters.private & filters.video)
async def check_token_or_premium(client, message: Message):
    user_id = message.from_user.id

    if await db.is_premium(user_id):
        return

    if await db.get_verified_token(user_id):
        return

    await message.reply_text(
        "**⚠️ প্রথমে টোকেন ভেরিফাই করতে হবে!**\n\nভেরিফাই না করলে ভিডিও রিনেম হবে না।",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ টোকেন ভেরিফাই করুন", url=f"https://tnlinks.in/X3trAsSG?user_id={user_id}")]]
        )
    )


@Client.on_message(filters.private & filters.command("verify"))
async def verify_token_command(client, message: Message):
    user_id = message.from_user.id
    await db.set_verified_token(user_id)
    await message.reply_text("✅ আপনি সফলভাবে টোকেন ভেরিফাই করেছেন। এখন ভিডিও রিনেম করতে পারবেন।")