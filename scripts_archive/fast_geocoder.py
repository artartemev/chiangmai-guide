import json
import re
import urllib.parse
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

PARENT_DIR = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28"
CACHE_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/maps_cache.json")
TARGET_FILES = ["result 3.json", "result 4.json", "result 5.json"]

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
    "hang dong": "Hang Dong",
    "mae rim": "Mae Rim",
    "mae sa": "Mae Rim",
    "mon jam": "Mae Rim",
    "mae on": "Mae On / Mae Kampong",
    "san kamphaeng": "Mae On / Mae Kampong",
    "san sai": "San Sai",
    "doi suthep": "Doi Suthep",
    "pai": "Pai / Chiang Dao",
    "chiang dao": "Pai / Chiang Dao",
    "chiang rai": "Pai / Chiang Dao"
}

maps_cache = {}
if os.path.exists(CACHE_PATH):
    try:
        maps_cache = json.load(open(CACHE_PATH, encoding="utf-8"))
    except Exception:
        maps_cache = {}

# Ensure OmHome is hardcoded
maps_cache["https://maps.app.goo.gl/FcH2vP9WtEEJqSM48"] = [
    "OmHome Space",
    "Pa Daet / Chang Khlan",
    "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
    18.7629,
    98.9955
]

def extract_text(obj):
    if isinstance(obj, str): return obj
    elif isinstance(obj, list): return "".join([extract_text(item) for item in obj])
    elif isinstance(obj, dict):
        if "text" in obj: return extract_text(obj["text"])
        elif "blocks" in obj: return "\n".join(filter(None, [extract_text(b) for b in obj["blocks"]]))
        elif "content" in obj: return extract_text(obj["content"])
    return ""

print("Collecting Google Maps links from target files...")
all_links = set()
for fname in TARGET_FILES:
    fpath = os.path.join(PARENT_DIR, fname)
    if not os.path.exists(fpath): continue
    data = json.load(open(fpath, encoding="utf-8"))
    for m in data.get("messages", []):
        txt = extract_text(m.get("text", "")).strip()
        m_match = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", txt)
        if m_match:
            u = m_match.group(0).rstrip(".,)")
            all_links.add(u)

print(f"Total unique Google Maps URLs collected: {len(all_links):,}")

# Filter out already valid entries
unresolved = []
for u in all_links:
    if u in maps_cache and maps_cache[u][0] and not maps_cache[u][0].replace('.', '').isdigit():
        continue
    unresolved.append(u)

print(f"Need resolution: {len(unresolved):,}")

lock = threading.Lock()

def resolve_single_url(url):
    try:
        r = requests.get(url, allow_redirects=False, timeout=5)
        loc = r.headers.get("location", "")
        if not loc and r.status_code == 200:
            # fallback: look inside text
            loc_m = re.search(r"https://www\.google\.com/maps/place/[^\s\"\'<>]+", r.text)
            if loc_m:
                loc = loc_m.group(0)

        if not loc:
            return (url, ["", "Other", "", 0.0, 0.0])

        p_m = re.search(r"/place/([^/@]+)", loc)
        q_m = re.search(r"[?&]q=([^&]+)", loc)
        c_m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", loc)
        d_m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", loc)

        lat, lng = 0.0, 0.0
        if c_m:
            lat, lng = float(c_m.group(1)), float(c_m.group(2))
        elif d_m:
            lat, lng = float(d_m.group(1)), float(d_m.group(2))

        query_str = ""
        if p_m:
            query_str = urllib.parse.unquote(p_m.group(1)).replace("+", " ")
        elif q_m:
            query_str = urllib.parse.unquote(q_m.group(1)).replace("+", " ")

        place_name = ""
        address = query_str
        neighborhood = "Other"

        if query_str:
            parts = [p.strip() for p in query_str.split(",")]
            if parts:
                place_name = parts[0]

            q_lower = query_str.lower()
            for sub, neigh in SUBDISTRICT_MAP.items():
                if sub in q_lower:
                    neighborhood = neigh
                    break

        return (url, [place_name, neighborhood, address, lat, lng])
    except Exception:
        return (url, ["", "Other", "", 0.0, 0.0])

# Resolve with 25 threads
resolved_count = 0
with ThreadPoolExecutor(max_workers=25) as executor:
    future_to_url = {executor.submit(resolve_single_url, u): u for u in unresolved}
    for i, f in enumerate(as_completed(future_to_url)):
        try:
            u, res = f.result()
            with lock:
                maps_cache[u] = res
                if res[0]:
                    resolved_count += 1
        except Exception:
            pass

        if (i + 1) % 100 == 0:
            with lock:
                snap = dict(maps_cache)
            with open(CACHE_PATH, "w", encoding="utf-8") as out:
                json.dump(snap, out, ensure_ascii=False, indent=2)
            print(f"Progress: {i + 1}/{len(unresolved)} processed ({resolved_count} newly resolved)...")

with lock:
    snap = dict(maps_cache)
with open(CACHE_PATH, "w", encoding="utf-8") as out:
    json.dump(snap, out, ensure_ascii=False, indent=2)

print(f"\n🎉 Resolution complete! Total cached entries: {len(maps_cache):,}")
