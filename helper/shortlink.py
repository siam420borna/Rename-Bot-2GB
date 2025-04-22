import aiohttp

API_KEY = "YOUR_TNLINK_API_KEY"  # এখানে তোমার tnlink.in API KEY বসাও

async def create_shortlink(user_id: int):
    long_url = f"https://yourdomain.com/verify?uid={user_id}"  # ভবিষ্যতে redirect system বসাতে পারো
    api_url = f"https://tnlink.in/api?api={API_KEY}&url={long_url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            try:
                data = await resp.json()
                return data["shortenedUrl"] if "shortenedUrl" in data else None
            except Exception as e:
                print(f"Shortlink error: {e}")
                return None