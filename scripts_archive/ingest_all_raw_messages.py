import json
import os
import glob
import sqlite3

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"
PARENT_DIR = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28"

def extract_text(obj):
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, list):
        return "".join([extract_text(item) for item in obj])
    elif isinstance(obj, dict):
        if "text" in obj:
            return extract_text(obj["text"])
        elif "blocks" in obj:
            return "\n".join(filter(None, [extract_text(b) for b in obj["blocks"]]))
        elif "items" in obj:
            return "\n".join(filter(None, [extract_text(it) for it in obj["items"]]))
        elif "content" in obj:
            return extract_text(obj["content"])
    return ""

def run_ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get existing (telegram_msg_id, channel_username) to prevent exact duplicates
    c.execute("SELECT telegram_msg_id, channel_username FROM reviews WHERE telegram_msg_id IS NOT NULL")
    existing_pairs = set(c.fetchall())
    print(f"Current reviews in DB: {len(existing_pairs)}")

    json_files = sorted(glob.glob(os.path.join(PARENT_DIR, "result*.json")))
    print(f"Found {len(json_files)} export files to process.")

    total_added = 0

    KEYWORDS = [
        "https://", "http://", "maps", "alltrails", "📍", "где", "кафе", "ресторан", "коворкинг",
        "водопад", "тропа", "хайк", "трек", "ивент", "фестиваль", "концерт", "воркшоп", "workshop",
        "omhome", "om home", "веган", "vegan", "кофе", "coffee", "bistro", "bakery", "park", "market",
        "встреча", "митап", "выходные", "суббота", "воскресенье", "пятница", "вечеринка", "party",
        "джаз", "музыка", "йога", "пилатес", "выставка", "ярмарка"
    ]

    for fpath in json_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        chat_name = data.get("name", fname)
        chat_id = data.get("id", "")
        msgs = data.get("messages", [])
        print(f"Processing {fname} (Chat: {chat_name}) - {len(msgs):,} messages...")

        added_for_file = 0
        for m in msgs:
            m_id = m.get("id")
            if not m_id:
                continue

            pair = (m_id, chat_name)
            if pair in existing_pairs:
                continue

            raw_text = extract_text(m.get("text", "")).strip()
            if not raw_text or len(raw_text) < 10:
                continue

            raw_lower = raw_text.lower()
            # Must contain a link or a candidate keyword
            if not any(k in raw_lower for k in KEYWORDS):
                continue

            sender = m.get("from") or m.get("actor") or chat_name
            msg_date = m.get("date", "").replace("T", " ")

            source_link = ""
            if chat_id:
                source_link = f"https://t.me/c/{chat_id}/{m_id}"

            c.execute("""
                INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
                VALUES (0, ?, ?, ?, ?, ?, '', ?)
            """, (m_id, chat_name, sender, msg_date, raw_text, source_link))

            existing_pairs.add(pair)
            added_for_file += 1
            total_added += 1

        print(f"  -> Added {added_for_file:,} review records from {fname}")

    conn.commit()

    c.execute("SELECT count(*) FROM reviews")
    final_count = c.fetchone()[0]
    conn.close()

    print(f"\n🎉 Ingestion complete! Total reviews in database: {final_count:,} (Newly added: {total_added:,})")

if __name__ == "__main__":
    run_ingest()
