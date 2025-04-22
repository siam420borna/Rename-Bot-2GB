import motor.motor_asyncio
from config import Config
from .utils import send_log
from config import Config
DB_URL = Config.DB_URL
DB_NAME = Config.DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.user_col = self.db["users"]
        self.banned_col = self.db["bannedList"]
        self.user_data = self.db["user_data"]
        self.config_col = self.db["config"]

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
            await self.user_col.insert_one(self.new_user(user.id))
            await send_log(bot, user)

    async def is_user_exist(self, user_id):
        return await self.user_col.find_one({'_id': int(user_id)}) is not None

    async def total_users_count(self):
        return await self.user_col.count_documents({})

    async def get_all_users(self):
        return self.user_col.find({})

    async def delete_user(self, user_id):
        await self.user_col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, user_id, file_id):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('file_id') if user else None

    async def set_thumb_size(self, user_id, size):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'thumb_size': size}})

    async def get_thumb_size(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('thumb_size') if user else None

    async def set_caption(self, user_id, caption):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'caption': caption}})

    async def get_caption(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('caption') if user else None

    async def set_prefix(self, user_id, prefix):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'prefix': prefix}})

    async def get_prefix(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('prefix') if user else None

    async def set_suffix(self, user_id, suffix):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'suffix': suffix}})

    async def get_suffix(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('suffix') if user else None

    async def set_metadata(self, user_id, status):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'metadata': status}})

    async def get_metadata(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('metadata') if user else None

    async def set_metadata_code(self, user_id, code):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'metadata_code': code}})

    async def get_metadata_code(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user.get('metadata_code') if user else None

    async def ban_user(self, user_id):
        exists = await self.banned_col.find_one({'banId': int(user_id)})
        if exists:
            return False
        await self.banned_col.insert_one({'banId': int(user_id)})
        return True

    async def is_banned(self, user_id):
        return await self.banned_col.find_one({'banId': int(user_id)}) is not None

    async def unban_user(self, user_id):
        result = await self.banned_col.find_one({'banId': int(user_id)})
        if result:
            await self.banned_col.delete_one({'banId': int(user_id)})
            return True
        return False

    async def add_premium(self, user_id):
        await self.user_col.update_one({'_id': int(user_id)}, {'$set': {'premium': True}}, upsert=True)

    async def remove_premium(self, user_id):
        await self.user_col.update_one({'_id': int(user_id)}, {'$unset': {'premium': ""}})

    async def is_premium(self, user_id):
        user = await self.user_col.find_one({'_id': int(user_id)})
        return user and user.get('premium', False)

    async def set_watermark(self, user_id, text):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'watermark': text}}, upsert=True)

    async def get_watermark(self, user_id):
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('watermark') if user else None

    async def del_watermark(self, user_id):
        await self.user_data.update_one({'_id': user_id}, {'$unset': {'watermark': ""}})

    async def set_watermark_size(self, user_id, size):
        if size:
            await self.user_data.update_one({'_id': user_id}, {'$set': {'font_size': size}}, upsert=True)
        else:
            await self.user_data.update_one({'_id': user_id}, {'$unset': {'font_size': ""}})

    async def get_watermark_size(self, user_id):
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('font_size', 36)

    async def is_premium_enabled(self):
        doc = await self.config_col.find_one({'_id': 'premium_config'})
        return doc and doc.get('enabled', False)

    async def set_premium_enabled(self, status: bool):
        await self.config_col.update_one(
            {'_id': 'premium_config'},
            {'$set': {'enabled': status}},
            upsert=True
        )


# Instantiate the database
db = Database(Config.DB_URL, Config.DB_NAME)
jishubotz = db