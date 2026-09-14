import sqlite3
import requests
import re
import urllib.parse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"
CACHE_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/maps_cache.json"

SUBDISTRICT_MAP = {
    "chang khlan": "Pa Daet / Chang Khlan",
    "pa daet": "Pa Daet / Chang Khlan",
    "padet": "Pa Daet / Chang Khlan",
    "chang moi": "Old City / Chang Moi",
    "phra sing": "Old City",
    "si phum": "Old City",
    "nimman": "Nimman",
    "suthep": "Chang Phueak / Suthep",
    "chang phueak": "Chang Phueak / Suthep",
    "chang phuak": "Chang Phueak / Suthep",
    "hang dong": "Hang Dong",
    "mae rim": "Mae Rim",
    "mae sa": "Mae Rim",
    "mae on": "Mae On / Mae Kampong",
    "san kamphaeng": "Mae On / Mae Kampong",
    "san sai": "San Sai",
    "doi suthep": "Doi Suthep",
    "pai": "Pai / Chiang Dao",
    "chiang dao": "Pai / Chiang Dao",
    "chiang rai": "Pai / Chiang Dao"
}

CACHE = {}
if os.path.exists(CACHE_PATH):
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            CACHE = json.load(f)
        print(f"Loaded {len(CACHE):,} cached Google Maps entries from maps_cache.json")
    except Exception:
        CACHE = {}

# Ensure OmHome maps cache is hardcoded correctly
CACHE["https://maps.app.goo.gl/FcH2vP9WtEEJqSM48"] = [
    "OmHome Space",
    "Pa Daet / Chang Khlan",
    "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
    18.7629,
    98.9955
]

import threading

cache_lock = threading.Lock()

def resolve_link(url):
    if not url:
        return (None, None, "", 0.0, 0.0)

    with cache_lock:
        if url in CACHE:
            val = CACHE[url]
            return tuple(val)

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        r = requests.get(url, allow_redirects=True, stream=True, headers=headers, timeout=4)
        final_url = r.url

        place_name = ""
        neighborhood = "Other"
        address = ""
        lat, lng = 0.0, 0.0

        q_match = re.search(r"[?&]q=([^&]+)", final_url)
        p_match = re.search(r"/place/([^/@]+)", final_url)
        c_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", final_url)
        d_match = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", final_url)
        q_coords = re.search(r"(-?\d{1,2}\.\d+)\s*,\s*(-?\d{2,3}\.\d+)", final_url)

        if c_match:
            try:
                lat = float(c_match.group(1))
                lng = float(c_match.group(2))
            except Exception:
                pass
        elif d_match:
            try:
                lat = float(d_match.group(1))
                lng = float(d_match.group(2))
            except Exception:
                pass
        elif q_coords:
            try:
                lat = float(q_coords.group(1))
                lng = float(q_coords.group(2))
            except Exception:
                pass

        query_str = ""
        if q_match:
            query_str = urllib.parse.unquote(q_match.group(1)).replace("+", " ")
        elif p_match:
            query_str = urllib.parse.unquote(p_match.group(1)).replace("+", " ")

        if query_str:
            address = query_str
            parts = [p.strip() for p in query_str.split(",")]
            if parts:
                place_name = parts[0]

            q_lower = query_str.lower()
            for sub, neigh in SUBDISTRICT_MAP.items():
                if sub in q_lower:
                    neighborhood = neigh
                    break

        res = [place_name, neighborhood, address, lat, lng]
        with cache_lock:
            CACHE[url] = res
        return tuple(res)
    except Exception:
        res = ["", "Other", "", 0.0, 0.0]
        with cache_lock:
            CACHE[url] = res
        return tuple(res)

def run_batch_geocoder():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, review_text FROM reviews WHERE review_text LIKE '%maps.app.goo.gl%' OR review_text LIKE '%goo.gl/maps%'")
    rows = cursor.fetchall()
    print(f"Found {len(rows):,} reviews with Google Maps links.")

    link_map = {}
    for r in rows:
        m = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", r["review_text"])
        if m:
            short_url = m.group(0).rstrip(".,)")
            link_map[r["id"]] = short_url

    unique_urls = list(set(link_map.values()))
    unresolved = [u for u in unique_urls if u not in CACHE or not CACHE[u][0]]
    print(f"Total unique Google Maps URLs: {len(unique_urls):,} (Unresolved: {len(unresolved):,})")

    resolved_count = 0
    if unresolved:
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(resolve_link, url): url for url in unresolved}
            for i, future in enumerate(as_completed(future_to_url)):
                try:
                    res = future.result()
                    if res[0]:
                        resolved_count += 1
                except Exception:
                    pass
                if (i + 1) % 50 == 0:
                    with cache_lock:
                        cache_snapshot = dict(CACHE)
                    with open(CACHE_PATH, "w", encoding="utf-8") as f:
                        json.dump(cache_snapshot, f, ensure_ascii=False, indent=2)
                    print(f"Progress: {i + 1}/{len(unresolved)} resolved...")

    with cache_lock:
        cache_snapshot = dict(CACHE)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache_snapshot, f, ensure_ascii=False, indent=2)

    print(f"✅ Pass 2 Complete! Resolved maps cache saved to maps_cache.json with {len(CACHE):,} total entries.")
    conn.close()

if __name__ == "__main__":
    run_batch_geocoder()
