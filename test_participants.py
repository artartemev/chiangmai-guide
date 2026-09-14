import asyncio
from telethon import TelegramClient

API_ID = 27784305
API_HASH = "4f3e696f0c035287a9716b07a78dfd18"
SESSION_PATH = "../telegram_sync.session"

async def main():
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start()
    
    try:
        parts = await client.get_participants('ru_chiangmai', limit=10)
        print(f"ru_chiangmai participants found: {len(parts)}")
        for p in parts:
            print(p.first_name)
    except Exception as e:
        print("ru_chiangmai error:", e)
        
    await client.disconnect()

asyncio.run(main())
