async def set_thumb_size(user_id, size):
    db[user_id]['thumb_size'] = size

async def get_thumb_size(user_id):
    return db[user_id].get('thumb_size', '400x300')  # Default
