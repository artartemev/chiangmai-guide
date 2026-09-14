import asyncio
import os
from telethon import TelegramClient

API_ID = 27784305
API_HASH = "4f3e696f0c035287a9716b07a78dfd18"
SESSION_PATH = "../telegram_sync.session"
AVATARS_DIR = "static/avatars"

os.makedirs(AVATARS_DIR, exist_ok=True)

async def main():
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start()
    
    chats_to_search = ['ru_chiangmai', 'ChiamgMaimy']
    search_queries = ["Дима", "Дмитрий", "Dima", "Dmitry", "Dmitriy"]
    found_users = {}
    
    for chat in chats_to_search:
        print(f"Fetching from {chat}...")
        for query in search_queries:
            try:
                participants = await client.get_participants(chat, search=query)
                for user in participants:
                    if user.id not in found_users:
                        found_users[user.id] = user
            except Exception as e:
                print(f"Error searching {query} in {chat}: {e}")

    print(f"Total unique found: {len(found_users)}")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ru" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Список Дим // Чиангмай</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #070707; color: #f5f5f0; font-family: monospace; }
        </style>
    </head>
    <body class="p-8">
        <h1 class="text-2xl text-[#ff2e2e] mb-6">Список всех Дим</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    """
    
    for user_id, user in found_users.items():
        name_parts = []
        if user.first_name: name_parts.append(user.first_name)
        if user.last_name: name_parts.append(user.last_name)
        full_name = " ".join(name_parts)
        
        name_lower = full_name.lower()
        if not any(q.lower() in name_lower or (user.username and q.lower() in user.username.lower()) for q in search_queries):
            continue
            
        username_html = f'<a href="https://t.me/{user.username}" target="_blank" class="text-blue-400 hover:underline">@{user.username}</a>' if user.username else '<span class="text-gray-500">Нет юзернейма</span>'
        
        photo_path = f"{AVATARS_DIR}/{user.id}.jpg"
        if not os.path.exists(photo_path):
            try:
                await client.download_profile_photo(user, file=photo_path)
            except Exception:
                pass
                
        img_src = f"/{photo_path}" if os.path.exists(photo_path) else "https://via.placeholder.com/150/111111/ff2e2e?text=D"
        
        html_content += f"""
        <div class="border border-[#242424] bg-[#181818] p-4 flex items-center space-x-4">
            <img src="{img_src}" alt="Avatar" class="w-16 h-16 rounded-full object-cover border border-[#383838]">
            <div>
                <div class="font-bold text-white text-lg">{full_name}</div>
                <div class="text-sm mt-1">{username_html}</div>
                <div class="text-xs text-gray-500 mt-1">ID: {user.id}</div>
            </div>
        </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open('static/dimas.html', 'w') as f:
        f.write(html_content)
    print("Wrote to static/dimas.html")
    await client.disconnect()

asyncio.run(main())
