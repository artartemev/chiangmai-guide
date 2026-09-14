import json
import os
import re

PARENT_DIR = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28"
CACHE_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/maps_cache.json")
TARGET_FILES = ["result 3.json", "result 4.json", "result 5.json"]

maps_cache = json.load(open(CACHE_PATH, encoding="utf-8"))
print(f"Loaded {len(maps_cache):,} cached Google Maps entries.")

def extract_text(obj):
    if isinstance(obj, str): return obj
    elif isinstance(obj, list): return "".join([extract_text(item) for item in obj])
    elif isinstance(obj, dict):
        if "text" in obj: return extract_text(obj["text"])
        elif "blocks" in obj: return "\n".join(filter(None, [extract_text(b) for b in obj["blocks"]]))
        elif "content" in obj: return extract_text(obj["content"])
    return ""

found_places = {}

for fname in TARGET_FILES:
    fpath = os.path.join(PARENT_DIR, fname)
    if not os.path.exists(fpath): continue
    data = json.load(open(fpath, encoding="utf-8"))
    msgs = data.get("messages", [])
    print(f"Scanning {fname} ({len(msgs):,} messages)...")
    for m in msgs:
        txt = extract_text(m.get("text", "")).strip()
        if not txt or len(txt) < 10: continue

        m_match = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", txt)
        at_match = re.search(r"https?://[\w\.-]*alltrails\.com/trail/[^\s,\)\"\']*", txt)

        if m_match:
            u = m_match.group(0).rstrip(".,)").split("?g_st=")[0]
            if u in maps_cache:
                p_name, p_neigh, p_addr, p_lat, p_lng = maps_cache[u][:5]
                if p_name and not re.match(r"^\d{1,2}\.\d+$", p_name.strip()) and len(p_name.strip()) >= 3:
                    if u not in found_places:
                        found_places[u] = {
                            "name": p_name,
                            "neighborhood": p_neigh,
                            "address": p_addr,
                            "lat": p_lat,
                            "lng": p_lng,
                            "reviews_count": 1,
                            "sample_review": txt[:100].replace("\n", " ")
                        }
                    else:
                        found_places[u]["reviews_count"] += 1
        elif at_match:
            u = at_match.group(0).rstrip(".,)")
            at_m = re.search(r"alltrails\.com/trail/[^/\s]+/[^/\s]+/([a-z0-9-]+)", u)
            trail_name = at_m.group(1).replace("-", " ").title() if at_m else "Hiking Trail"
            if u not in found_places:
                found_places[u] = {
                    "name": trail_name,
                    "neighborhood": "Doi Suthep",
                    "address": "",
                    "lat": 0.0,
                    "lng": 0.0,
                    "reviews_count": 1,
                    "sample_review": txt[:100].replace("\n", " ")
                }
            else:
                found_places[u]["reviews_count"] += 1

print(f"\n✅ Total Verified Unique Places Found with Links: {len(found_places):,}")
top_places = sorted(found_places.values(), key=lambda x: x["reviews_count"], reverse=True)
for p in top_places[:20]:
    print(f" - {p['name']} ({p['neighborhood']}) : {p['reviews_count']} mentions | Addr: {p['address'][:40]}")
