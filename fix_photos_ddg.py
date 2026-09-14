import sqlite3
import os
import time
import requests
from duckduckgo_search import DDGS

conn = sqlite3.connect('chiangmai_guide.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title, category FROM items")
items = cursor.fetchall()
conn.close()

def download_image(url, filepath):
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

print(f"Checking {len(items)} items to replace generic photos with real DDG photos...")

count = 0
with DDGS() as ddgs:
    for item_id, title, category in items:
        filepath = f"static/photos/places/{item_id}.jpg"
        
        if os.path.exists(filepath):
            query = f"{title} Chiang Mai"
            try:
                results = list(ddgs.images(query, max_results=2))
                # try downloading the first, if fails try second
                for res in results:
                    img_url = res.get("image")
                    if img_url and download_image(img_url, filepath):
                        count += 1
                        if count % 10 == 0:
                            print(f"Replaced {count} photos so far...")
                        break
                time.sleep(0.5)
            except Exception as e:
                time.sleep(2)

print(f"Successfully replaced {count} photos with real DDG images!")
