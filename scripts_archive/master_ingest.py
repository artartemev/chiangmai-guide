import json
import os
import glob
import sqlite3

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"
PARENT_DIR = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28"

# Target files requested by user (EXCLUDING result.json and result 2.json)
TARGET_FILES = ["result 3.json", "result 4.json", "result 5.json"]

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

def run_selective_ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Clear reviews table for fresh selective ingestion
    c.execute("DELETE FROM reviews")
    c.execute("DELETE FROM sqlite_sequence WHERE name = 'reviews'")
    conn.commit()

    existing_pairs = set()
    total_added = 0

    KEYWORDS = [
        "https://", "http://", "maps", "alltrails", "📍", "где", "кафе", "ресторан", "коворкинг",
        "водопад", "тропа", "хайк", "трек", "ивент", "фестиваль", "концерт", "воркшоп", "workshop",
        "omhome", "om home", "веган", "vegan", "кофе", "coffee", "bistro", "bakery", "park", "market",
        "встреча", "митап", "выходные", "суббота", "воскресенье", "пятница", "вечеринка", "party",
        "джаз", "музыка", "йога", "пилатес", "выставка", "ярмарка"
    ]

    for fname in TARGET_FILES:
        fpath = os.path.join(PARENT_DIR, fname)
        if not os.path.exists(fpath):
            print(f"⚠️ Target file {fname} not found!")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        chat_name = data.get("name", fname)
        chat_id = data.get("id", "")
        msgs = data.get("messages", [])
        print(f"📖 Reading {fname} (Chat: {chat_name}) - {len(msgs):,} messages...")

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

        print(f"  ✅ Added {added_for_file:,} candidate reviews from {fname}")

    conn.commit()

    c.execute("SELECT count(*) FROM reviews")
    final_count = c.fetchone()[0]
    conn.close()

    print(f"\n🎉 Pass 1 Complete! Total selective candidate reviews in DB: {final_count:,}")

if __name__ == "__main__":
    run_selective_ingest()
