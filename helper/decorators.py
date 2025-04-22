from functools import wraps
from pyrogram.types import Message
from helper.database import jishubotz

def premium_feature(func):
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        # চেক করো প্রিমিয়াম মোড চালু আছে কিনা
        if await jishubotz.is_premium_enabled():
            # প্রিমিয়াম মোড অন থাকলে, ইউজার প্রিমিয়াম কিনা যাচাই করো
            if not await jishubotz.is_premium(message.from_user.id):
                return await message.reply("❌ এই ফিচারটি শুধু প্রিমিয়াম ইউজারদের জন্য।")
        # প্রিমিয়াম মোড অফ থাকলে অথবা ইউজার প্রিমিয়াম হলে ফিচার কাজ করবে
        return await func(client, message, *args, **kwargs)
    return wrapper