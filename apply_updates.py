"""
Bring chiangmai_guide.db to the current site state and export the static JSON.

Idempotent and safe to run after every daily_digest.py: it only touches what is
missing (coordinates, tags, ingested places, curated lists) and re-applies the
few manual curation decisions kept in this file. Order matters.

    python3 apply_updates.py           # normal daily run
    python3 apply_updates.py --no-net  # skip Google lookups (offline)
"""
import json
import math
import sqlite3
import subprocess
import sys

DB = "chiangmai_guide.db"
PY = sys.executable

# --- manual curation (by stable keys, never by autoincrement ids of new rows) ---
ARCHIVE_PLACE_IDS = {  # Google place id -> reason
    "0x30da3ba5dae6ebaf:0x7284726feade7cbe": "Loud Bar link points to a cannabis store",
}
ARCHIVE_ITEM_IDS = [  # existing catalogue rows reviewed by hand (ids are stable on main)
    521,  # "Air Purifier Cafes (Community List)" — a list, not a place
    439, 464, 481, 161, 135, 276, 383, 382, 258, 422, 470, 252,  # unrated / low-signal clinics, stays, spa
]
KEEP_ACTIVE_IDS = [10]  # Pun Pun vegetarian cafe: no Google link, but a known place
RECATEGORIZE = {207: ("nature", ["храмы"]), 253: ("nature", ["парки и сады"])}
TITLE_FIXES = {  # by Google place id, for ingested rows with messy Google names
    "0x30da476efedcb06d:0xf02a2e6ea2edfc69": "Klin Ai Mok Homestay (กลิ่นไอหมอก โฮมสเตย์)",
}
RENAME_CONTAINS = [  # (substring in title, new title)
    ('("Японец")', "Sri Sitthiphot Motor («Японец»)"),
    ("Aladdin Studio Chiang Mai", "Aladdin Studio (Workshop & Art Center)"),
    ("Mr. Mechanic Shop No.2", "Mr. Mechanic Shop No. 2"),
]


# Places that exist only as event venues but deserve a card of their own.
ENSURE_PLACES = [
    {
        "url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
        "title": "OmHome Space",
        "category": "workspace",
        "neighborhood": "Night Bazaar / Chang Khlan",
        "veg_friendly": 1,
        "website": "https://navito.omhome.space",
        "description": "Комьюнити-пространство в районе Chang Khlan, где рождается этот гид. Чайные церемонии с коллекционными улунами, киртаны и медитации, киновечера, квизы, настольные игры, йога-нидра, воркшопы — почти каждый вечер что-то происходит, расписание в Афише. Днём — тихое место поработать за чашкой чая.",
        "community_summary": {
            "highlights": ["Самая активная площадка русскоязычного комьюнити: 15+ событий в каталоге", "Чайная культура: дегустации высокогорных улунов и пуэров"],
            "pricing": ["Большинство вечеров — по донату или 200–400 THB"],
            "tips": ["Следите за анонсами в Афише; на популярные вечера лучше писать заранее", "Отзывы, правки и идеи для гида — t.me/artartemev"],
        },
    },
]


def ensure_places(conn, net):
    import geocode
    from datetime import datetime
    for p in ENSURE_PLACES:
        if conn.execute("SELECT 1 FROM items WHERE location_url LIKE ? || '%' AND category != 'event'", (p["url"],)).fetchone():
            continue
        res = geocode.resolve(p["url"]) if net else None
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO items (title, category, neighborhood, description, location_url, address, latitude, longitude,
               phone_contact, website, opening_hours, rating, rating_count, google_category, place_id, veg_friendly,
               mention_count, photos_json, community_summary, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, '[]', ?, ?, ?)""",
            (p["title"], p["category"], p["neighborhood"], p["description"], p["url"],
             (res or {}).get("address", ""), (res or {}).get("lat", 0), (res or {}).get("lng", 0),
             (res or {}).get("phone", ""), p.get("website") or (res or {}).get("website", ""),
             json.dumps(res["hours"], ensure_ascii=False) if res and res.get("hours") else "",
             (res or {}).get("rating"), (res or {}).get("rating_count"), (res or {}).get("gcategory"), (res or {}).get("place_id"),
             p.get("veg_friendly", 0),
             conn.execute("SELECT count(*) FROM items WHERE category='event' AND venue_name LIKE ?", (f"%{p['title']}%",)).fetchone()[0] or 1,
             json.dumps(p["community_summary"], ensure_ascii=False), now, now))
        conn.commit()
        print(f"  + place {p['title']}")


def run(script, *args):
    print(f"\n== {script} {' '.join(args)}")
    subprocess.run([PY, script, *args], check=True)


def ensure_schema(conn):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(items)")}
    for name, ddl in [("status", "TEXT DEFAULT 'active'"), ("tags", "TEXT DEFAULT '[]'"), ("rating", "REAL"),
                      ("rating_count", "INTEGER"), ("google_category", "TEXT"), ("place_id", "TEXT")]:
        if name not in cols:
            conn.execute(f"ALTER TABLE items ADD COLUMN {name} {ddl}")
    ccols = {r[1] for r in conn.execute("PRAGMA table_info(collections)")}
    if "kind" not in ccols:
        conn.execute("ALTER TABLE collections ADD COLUMN kind TEXT DEFAULT 'route'")
    conn.execute("UPDATE items SET status = 'active' WHERE status IS NULL")
    conn.commit()


def curate(conn):
    print("\n== manual curation")
    for pid in ARCHIVE_PLACE_IDS:
        conn.execute("UPDATE items SET status='archived' WHERE place_id = ?", (pid,))
    conn.execute(f"UPDATE items SET status='archived' WHERE id IN ({','.join('?' * len(ARCHIVE_ITEM_IDS))})", ARCHIVE_ITEM_IDS)
    conn.execute(f"UPDATE items SET status='active' WHERE id IN ({','.join('?' * len(KEEP_ACTIVE_IDS))})", KEEP_ACTIVE_IDS)
    for iid, (cat, tags) in RECATEGORIZE.items():
        conn.execute("UPDATE items SET category=?, tags=? WHERE id=?", (cat, json.dumps(tags, ensure_ascii=False), iid))
    for pid, title in TITLE_FIXES.items():
        conn.execute("UPDATE items SET title=? WHERE place_id=?", (title, pid))
    for needle, title in RENAME_CONTAINS:
        conn.execute("UPDATE items SET title=? WHERE title LIKE ?", (title, f"%{needle}%"))
    conn.execute("UPDATE items SET title = replace(title, char(8203), '')")  # zero-width spaces from Thai names
    conn.execute("UPDATE collections SET kind='collection' WHERE title='Путь Вегана'")
    conn.commit()


def archive_low_signal(conn):
    """Rule-based archive: one chat message or less, not in any collection, weak Google signal."""
    sql = """
    WITH x AS (
      SELECT i.id,
             (SELECT count(*) FROM reviews r WHERE r.item_id = i.id) AS rc,
             EXISTS(SELECT 1 FROM collection_items ci WHERE ci.item_id = i.id) AS incol,
             EXISTS(SELECT 1 FROM reviews r WHERE r.item_id = i.id AND r.review_text LIKE 'Из списка%') AS from_list
      FROM items i WHERE i.category != 'event' AND i.status = 'active')
    UPDATE items SET status = 'archived'
    WHERE id IN (SELECT id FROM x WHERE rc <= 1 AND incol = 0 AND from_list = 0)
      AND (rating IS NULL OR rating < 4.3 OR (rating < 4.6 AND COALESCE(rating_count, 0) < 40))
    """
    before = conn.execute("SELECT count(*) FROM items WHERE status='archived'").fetchone()[0]
    conn.execute(sql)
    conn.commit()
    after = conn.execute("SELECT count(*) FROM items WHERE status='archived'").fetchone()[0]
    print(f"\n== archive rule: +{after - before} (total archived {after})")


def fill_neighborhoods(conn):
    known = conn.execute("SELECT neighborhood, latitude, longitude FROM items WHERE latitude != 0 AND neighborhood != 'Other' AND category != 'event'").fetchall()
    todo = conn.execute("SELECT id, latitude, longitude FROM items WHERE latitude != 0 AND neighborhood = 'Other'").fetchall()
    n = 0
    for iid, la, lo in todo:
        near = sorted(((111 * math.hypot(a - la, (b - lo) * math.cos(math.radians(la))), nb) for nb, a, b in known))[:5]
        votes = {}
        for d, nb in near:
            if d < 2.5:
                votes[nb] = votes.get(nb, 0) + 1
        if votes:
            conn.execute("UPDATE items SET neighborhood=? WHERE id=?", (max(votes, key=votes.get), iid))
            n += 1
    conn.commit()
    print(f"\n== neighborhoods assigned to {n} places")


def main():
    net = "--no-net" not in sys.argv
    conn = sqlite3.connect(DB)
    ensure_schema(conn)
    conn.close()

    conn = sqlite3.connect(DB)
    ensure_places(conn, net)
    conn.close()

    if net:
        run("geocode.py")                              # coordinates/rating/hours for rows that lack them
        run("ingest_lists.py", "data/chat_lists.json")  # curated chat lists (skips places already present)

    run("seed_collections.py")
    run("tag_items.py")

    conn = sqlite3.connect(DB)
    curate(conn)            # after tag_items so explicit tags/categories win
    archive_low_signal(conn)
    fill_neighborhoods(conn)
    conn.close()

    run("update_wiki.py")
    run("export_static.py")


if __name__ == "__main__":
    main()
