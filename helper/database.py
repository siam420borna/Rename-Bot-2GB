import os
import asyncio

import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.jishubotz = self._client[database_name]
        self.col = self.jishubotz.user
        self.bannedList = self.jishubotz.bannedList
        self.user_col = self.jishubotz.users
        self.user_data = self.jishubotz.user_data

    def new_user(self, id):
        return {
            '_id': int(id),
            'file_id': None,
            'batch_mode': False,
            'caption': None,
            'prefix': None,
            'suffix': None,
            'metadata': False,
            'metadata_code': 'By :- @TechifyBots'
        }

    async def add_user(self, bot, message):
        user = message.from_user
        if not await self.is_user_exist(user.id):
            await self.col.insert_one(self.new_user(user.id))
            await send_log(bot, user)

    async def is_user_exist(self, id):
        return await self.col.find_one({'_id': int(id)}) is not None

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id') if user else None

    async def set_thumb_size(self, id, size):
        await self.col.update_one({'_id': int(id)}, {'$set': {'thumb_size': size}})

    async def get_thumb_size(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('thumb_size') if user else None

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption') if user else None

    async def set_prefix(self, id, prefix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'prefix': prefix}})

    async def get_prefix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('prefix') if user else None

    async def set_suffix(self, id, suffix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'suffix': suffix}})

    async def get_suffix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('suffix') if user else None

    async def set_metadata(self, id, bool_meta):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata': bool_meta}})

    async def get_metadata(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata') if user else None

    async def set_metadata_code(self, id, metadata_code):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata_code': metadata_code}})

    async def get_metadata_code(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata_code') if user else None

    async def ban_user(self, user_id):
        exists = await self.bannedList.find_one({'banId': int(user_id)})
        if exists:
            return False
        await self.bannedList.insert_one({'banId': int(user_id)})
        return True

    async def is_banned(self, user_id):
        return await self.bannedList.find_one({'banId': int(user_id)}) is not None

    async def is_unbanned(self, user_id):
        result = await self.bannedList.find_one({'banId': int(user_id)})
        if result:
            await self.bannedList.delete_one({'banId': int(user_id)})
            return True
        return False

    async def add_premium(self, user_id: int):
        await self.user_col.update_one({"_id": user_id}, {"$set": {"premium": True}}, upsert=True)

    async def remove_premium(self, user_id: int):
        await self.user_col.update_one({"_id": user_id}, {"$unset": {"premium": ""}})

    async def is_premium(self, user_id: int) -> bool:
        user = await self.user_col.find_one({"_id": user_id})
        return user and user.get("premium", False)

# Extra watermark functions
async def set_watermark(user_id, text):
    await db.user_data.update_one({"_id": user_id}, {"$set": {"watermark": text}}, upsert=True)

async def get_watermark(user_id):
    user = await db.user_data.find_one({"_id": user_id})
    return user.get("watermark") if user else None

async def del_watermark(user_id):
    await db.user_data.update_one({"_id": user_id}, {"$unset": {"watermark": ""}})

async def set_watermark_size(user_id, size):
    if size:
        await db.user_data.update_one({"_id": user_id}, {"$set": {"font_size": size}})
    else:
        await db.user_data.update_one({"_id": user_id}, {"$unset": {"font_size": ""}})

async def get_watermark_size(user_id):
    user = await db.user_data.find_one({"_id": user_id})
    return user.get("font_size", 36)

# Instantiate
jishubotz = Database(Config.DB_URL, Config.DB_NAME)
db = jishubotz.jishubotz



# Premium System ON আছে কিনা চেক করা
async def is_premium_enabled(self) -> bool:
    data = await self.config_col.find_one({"_id": "premium_system"})
    return data and data.get("enabled", False)

# Premium System ON/OFF করা
async def toggle_premium(self, status: bool):
    await self.config_col.update_one({"_id": "premium_system"}, {"$set": {"enabled": status}}, upsert=True)