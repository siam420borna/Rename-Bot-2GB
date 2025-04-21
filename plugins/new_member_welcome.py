from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.new_chat_members)
async def welcome_new_member(client, message: Message):
    for member in message.new_chat_members:
        if member.is_bot:
            continue

        name = member.first_name or "নাম নেই"
        username = f"@{member.username}" if member.username else "Username নেই"
        user_id = member.id

        try:
            photos = await client.get_profile_photos(user_id, limit=1)
            if photos.total_count > 0:
                photo_file = await client.download_media(photos[0])
                await message.reply_photo(
                    photo=photo_file,
                    caption=(
                        f"স্বাগতম {name}!\n\n"
                        f"➡️ ইউজারনেম: {username}\n"
                        f"🆔 ইউজার আইডি: `{user_id}`\n\n"
                        "আশা করি তুমি আমাদের সাথে ভালো সময় কাটাবে!"
                    )
                )
            else:
                raise Exception("No photo")
        except Exception as e:
            await message.reply_text(
                f"স্বাগতম {name}!\n\n"
                f"➡️ ইউজারনেম: {username}\n"
                f"🆔 ইউজার আইডি: `{user_id}`\n\n"
                "আশা করি তুমি আমাদের সাথে ভালো সময় কাটাবে!"
            )