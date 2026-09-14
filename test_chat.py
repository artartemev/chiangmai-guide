import asyncio
from telethon import TelegramClient

API_ID = 27784305
API_HASH = "4f3e696f0c035287a9716b07a78dfd18"
SESSION_PATH = "../telegram_sync.session"

async def main():
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start()
    
    try:
        entity = await client.get_entity('ru_chiangmai')
        print(f"Chat title: {entity.title}")
        print(f"Participants count: {entity.participants_count}")
        print(f"Is channel? {entity.broadcast}")
        print(f"Is megagroup? {entity.megagroup}")
    except Exception as e:
        print("ru_chiangmai error:", e)
        
    await client.disconnect()

asyncio.run(main())
