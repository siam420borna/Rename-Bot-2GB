import os
import asyncio
import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:
    def __init__(self, uri, db_name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.users = self.db.users
        self.banned = self.db.banned

    def new_user(self, user_id):
        return {
            "_id": int(user_id),
            "file_id": None,
            "thumb_size": None,
            "caption": None,
            "prefix": None,
            "suffix": None,
            "metadata": False,
            "metadata_code": "By :- @TechifyBots",
            "watermark": None,
            "font_size": 36,
            "premium": False
        }

    async def add_user(self, bot, message):
        user = message.from_user
        if not await self.users.find_one({"_id": user.id}):
            await self.users.insert_one(self.new_user(user.id))
            await send_log(bot, user)

    async def is_user_exist(self, user_id):
        return await self.users.find_one({"_id": int(user_id)}) is not None

    async def get_user(self, user_id):
        return await self.users.find_one({"_id": int(user_id)})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    async def delete_user(self, user_id):
        await self.users.delete_one({"_id": int(user_id)})

    # Thumbnail
    async def set_thumbnail(self, user_id, file_id):
        await self.users.update_one({"_id": user_id}, {"$set": {"file_id": file_id}})

    async def get_thumbnail(self, user_id):
        user = await self.get_user(user_id)
        return user.get("file_id") if user else None

    async def set_thumb_size(self, user_id, size):
        await self.users.update_one({"_id": user_id}, {"$set": {"thumb_size": size}})

    async def get_thumb_size(self, user_id):
        user = await self.get_user(user_id)
        return user.get("thumb_size") if user else None

    # Caption / Prefix / Suffix
    async def set_caption(self, user_id, caption):
        await self.users.update_one({"_id": user_id}, {"$set": {"caption": caption}})

    async def get_caption(self, user_id):
        user = await self.get_user(user_id)
        return user.get("caption") if user else None

    async def set_prefix(self, user_id, prefix):
        await self.users.update_one({"_id": user_id}, {"$set": {"prefix": prefix}})

    async def get_prefix(self, user_id):
        user = await self.get_user(user_id)
        return user.get("prefix") if user else None

    async def set_suffix(self, user_id, suffix):
        await self.users.update_one({"_id": user_id}, {"$set": {"suffix": suffix}})

    async def get_suffix(self, user_id):
        user = await self.get_user(user_id)
        return user.get("suffix") if user else None

    # Metadata
    async def set_metadata(self, user_id, status):
        await self.users.update_one({"_id": user_id}, {"$set": {"metadata": status}})

    async def get_metadata(self, user_id):
        user = await self.get_user(user_id)
        return user.get("metadata") if user else None

    async def set_metadata_code(self, user_id, code):
        await self.users.update_one({"_id": user_id}, {"$set": {"metadata_code": code}})

    async def get_metadata_code(self, user_id):
        user = await self.get_user(user_id)
        return user.get("metadata_code") if user else None

    # Watermark Text & Font Size
    async def set_watermark(self, user_id, text):
        await self.users.update_one({"_id": user_id}, {"$set": {"watermark": text}})

    async def get_watermark(self, user_id):
        user = await self.get_user(user_id)
        return user.get("watermark") if user else None

    async def del_watermark(self, user_id):
        await self.users.update_one({"_id": user_id}, {"$unset": {"watermark": ""}})

    async def set_watermark_size(self, user_id, size):
        if size:
            await self.users.update_one({"_id": user_id}, {"$set": {"font_size": size}})
        else:
            await self.users.update_one({"_id": user_id}, {"$unset": {"font_size": ""}})

    async def get_watermark_size(self, user_id):
        user = await self.get_user(user_id)
        return user.get("font_size", 36)

    # Premium
    async def add_premium(self, user_id):
        await self.users.update_one({"_id": user_id}, {"$set": {"premium": True}}, upsert=True)

    async def remove_premium(self, user_id):
        await self.users.update_one({"_id": user_id}, {"$unset": {"premium": ""}})

    async def is_premium(self, user_id):
        user = await self.get_user(user_id)
        return user.get("premium", False) if user else False

    # Ban System
    async def ban_user(self, user_id):
        if await self.banned.find_one({"banId": user_id}):
            return False
        await self.banned.insert_one({"banId": user_id})
        return True

    async def is_banned(self, user_id):
        return await self.banned.find_one({"banId": user_id}) is not None

    async def unban_user(self, user_id):
        result = await self.banned.find_one({"banId": user_id})
        if result:
            await self.banned.delete_one({"banId": user_id})
            return True
        return False


# Instantiate
db = Database(Config.DB_URL, Config.DB_NAME)