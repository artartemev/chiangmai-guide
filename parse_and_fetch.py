import asyncio
import json
import os
from telethon import TelegramClient
from telethon.tl.types import User

API_ID = 27784305
API_HASH = "4f3e696f0c035287a9716b07a78dfd18"
SESSION_PATH = "../telegram_sync.session"
AVATARS_DIR = "static/avatars"

os.makedirs(AVATARS_DIR, exist_ok=True)

search_queries = ["дима", "дмитрий", "dima", "dmitry", "dmitriy"]
dimas_data = {}

print("Parsing JSON...")
with open('../result.json', 'r') as f:
    data = json.load(f)
    for msg in data.get('messages', []):
        sender = msg.get('from')
        if not sender: continue
        name_lower = sender.lower()
        if any(q in name_lower for q in search_queries):
            uid = msg.get('from_id')
            if uid and str(uid).startswith('user'):
                num_id = int(str(uid).replace('user', ''))
                if num_id not in dimas_data:
                    dimas_data[num_id] = {"name": sender, "id": num_id, "username": None, "avatar": None}

print(f"Found {len(dimas_data)} user IDs in JSON.")

async def main():
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start()
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ru" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dima Database</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #070707; color: #f5f5f0; font-family: monospace; }
        </style>
    </head>
    <body class="p-8">
        <h1 class="text-2xl text-[#ff2e2e] mb-2"><i class="fa-solid fa-users"></i> DIMA DATABASE</h1>
        <p class="text-gray-400 mb-6">Список пользователей с именем Дима/Дмитрий, замеченных в чате.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    """
    
    fetched = 0
    for uid, info in dimas_data.items():
        try:
            # We use get_entity. If it fails, we fall back to JSON data.
            user = await client.get_entity(uid)
            if isinstance(user, User):
                name_parts = []
                if user.first_name: name_parts.append(user.first_name)
                if user.last_name: name_parts.append(user.last_name)
                info["name"] = " ".join(name_parts)
                info["username"] = user.username
                
                photo_path = f"{AVATARS_DIR}/{user.id}.jpg"
                if not os.path.exists(photo_path):
                    try:
                        await client.download_profile_photo(user, file=photo_path)
                    except: pass
                if os.path.exists(photo_path):
                    info["avatar"] = f"/{photo_path}"
                fetched += 1
        except Exception:
            pass # Fallback to JSON data
            
        full_name = info["name"]
        username_html = f'<a href="https://t.me/{info["username"]}" target="_blank" class="text-blue-400 hover:underline">@{info["username"]}</a>' if info["username"] else '<span class="text-gray-600">@unknown</span>'
        img_src = info["avatar"] if info["avatar"] else f"https://ui-avatars.com/api/?name={full_name.replace(' ', '+')}&background=181818&color=ff2e2e"
        
        html_content += f"""
        <div class="border border-[#242424] bg-[#181818] p-4 flex items-center space-x-4 hover:border-[#383838] transition">
            <img src="{img_src}" alt="Avatar" class="w-12 h-12 rounded-full object-cover border border-[#383838]">
            <div>
                <div class="font-bold text-white text-sm">{full_name}</div>
                <div class="text-xs mt-1">{username_html}</div>
                <div class="text-[10px] text-gray-500 mt-1">ID: {uid}</div>
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
    print(f"Successfully generated HTML with {len(dimas_data)} profiles ({fetched} enriched via Telethon).")
    await client.disconnect()

asyncio.run(main())
