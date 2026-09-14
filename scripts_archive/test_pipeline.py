import sqlite3
import json
import re
import urllib.parse
from datetime import datetime

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"
CACHE_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/maps_cache.json"
CH_POSTS_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiamgmaimy_posts.json"

MAPS_CACHE = {}
if open(CACHE_PATH):
    MAPS_CACHE = json.load(open(CACHE_PATH, encoding="utf-8"))

print(f"Loaded {len(MAPS_CACHE):,} Google Maps cache entries.")

# Load ChiamgMaimy posts
ch_posts = []
try:
    ch_posts = json.load(open(CH_POSTS_PATH, encoding="utf-8"))
    print(f"Loaded {len(ch_posts):,} posts from @ChiamgMaimy.")
except Exception as e:
    print("Error loading ChiamgMaimy posts:", e)

# Test parsing
print("Done test init.")
