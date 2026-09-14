"""
Add places from curated chat lists (name + Google Maps link) to the catalog.

Input: a JSON file {list_key: {msg, date, from, items: [[note, url], ...]}}
produced from the Telegram export. Each link is resolved through geocode.py,
so new items arrive with coordinates, official name, rating, phone and hours.
Items whose Google place id already exists in the DB are skipped.

Usage: python3 ingest_lists.py lists.json
"""
import json
import math
import sqlite3
import sys
from datetime import datetime

import geocode

DB = "chiangmai_guide.db"
CHAT_LINK = "https://t.me/ru_chiangmai/{}"

LIST_META = {
    "glamping": {"category": "stay", "intro": "Глэмпинг / ночёвка в горах недалеко от Чиангмая. Из списка глэмпингов, который собрали участники чата."},
    "rentals": {"category": "services", "intro": "Прокат байков и мотоциклов. Из сводного списка ренталов, который составили участники чата — по телефону обычно доступен Line."},
    "workshops": {"category": "services", "intro": "Воркшоп / мастер-класс. Из подборки участников чата «какие воркшопы есть в Чиангмае»."},
}


def nearest_neighborhood(conn, lat, lng):
    best, best_d = "Other", 4.0
    for n, la, lo in conn.execute("SELECT neighborhood, latitude, longitude FROM items WHERE latitude != 0 AND neighborhood != 'Other'"):
        d = 111 * math.hypot(la - lat, (lo - lng) * math.cos(math.radians(lat)))
        if d < best_d:
            best, best_d = n, d
    return best


def main(path):
    lists = json.load(open(path, encoding="utf-8"))
    conn = sqlite3.connect(DB)
    geocode.ensure_columns(conn)
    existing_pids = {r[0] for r in conn.execute("SELECT place_id FROM items WHERE place_id IS NOT NULL")}
    now = datetime.now().isoformat(timespec="seconds")
    added = skipped = failed = 0

    for key, block in lists.items():
        meta = LIST_META[key]
        for note, url in block["items"]:
            res = geocode.resolve(url)
            if not res:
                failed += 1
                print(f"  ✗ {key}: {note or url}")
                continue
            if res["place_id"] in existing_pids:
                skipped += 1
                continue
            gname = res.get("name") or res["address"].split(",", 1)[0].strip()
            note_clean = note.strip(" -–:")
            # Title: official Google name; keep the chat's wording as a hint when it differs
            title = gname if gname else note_clean
            if note_clean and note_clean.lower() not in gname.lower() and not any(ch in note_clean for ch in "🎂🎨🪡🏺💍💼") and len(note_clean) < 40:
                title = f"{gname} ({note_clean})" if gname else note_clean
            desc = meta["intro"]
            if note_clean and note_clean.lower() != gname.lower():
                desc += f"\n\nИз чата: «{note_clean}»."
            if res.get("gcategory"):
                desc += f"\nКатегория в Google: {res['gcategory']}."
            neigh = nearest_neighborhood(conn, res["lat"], res["lng"])
            cur = conn.execute(
                """INSERT INTO items (title, category, neighborhood, description, location_url, address, latitude, longitude,
                   phone_contact, website, opening_hours, rating, rating_count, google_category, place_id,
                   mention_count, photos_json, community_summary, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,'[]',NULL,?,?)""",
                (title, meta["category"], neigh, desc, url.split("?")[0], res["address"], res["lat"], res["lng"],
                 res.get("phone", ""), res.get("website", ""),
                 json.dumps(res["hours"], ensure_ascii=False) if res.get("hours") else "",
                 res.get("rating"), res.get("rating_count"), res.get("gcategory"), res["place_id"], now, now))
            item_id = cur.lastrowid
            conn.execute(
                """INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (item_id, block["msg"], "@ru_chiangmai", block["from"], block["date"],
                 f"Из списка «{key}»: {note_clean or gname}", "", CHAT_LINK.format(block["msg"])))
            conn.commit()
            existing_pids.add(res["place_id"])
            added += 1
            print(f"  + {title} [{neigh}] ★{res.get('rating')}")
    print(f"Added {added}, skipped {skipped} (already in DB), failed {failed}.")


if __name__ == "__main__":
    main(sys.argv[1])
