import json
import os
import sys
from database import init_db, get_db
from llm_extractor import extract_with_llm
from deduplicator import process_and_save_entity, archive_past_events

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

def ingest_from_json(json_filename):
    filepath = os.path.join(PARENT_DIR, json_filename)
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        return 0
        
    print(f"📖 Processing {json_filename}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    channel_name = data.get("name", "visadtv")
    msgs = data.get("messages", [])
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT msg_id FROM processed_messages")
    processed_set = set(row[0] for row in cursor.fetchall())
    conn.close()
    
    saved_count = 0
    for idx, m in enumerate(msgs):
        m_id = m.get("id")
        if not m_id or m_id in processed_set:
            continue
            
        raw_text = extract_text(m.get("text", "")).strip()
        if not raw_text or len(raw_text) < 15:
            continue
            
        entity = extract_with_llm(raw_text)
        if entity and entity.get("has_entity"):
            review_meta = {
                "msg_id": m_id,
                "channel": channel_name,
                "sender": m.get("from") or m.get("actor") or "Система",
                "date": m.get("date", "").replace("T", " "),
                "text": raw_text,
                "reactions": "",
                "source_link": f"https://t.me/visadtv/{m_id}"
            }
            saved_id = process_and_save_entity(entity, review_meta)
            if saved_id:
                saved_count += 1
                
        conn = get_db()
        conn.cursor().execute("INSERT OR IGNORE INTO processed_messages (msg_id, channel, processed_at) VALUES (?, ?, ?)", (m_id, channel_name, m.get("date")))
        conn.commit()
        conn.close()
        processed_set.add(m_id)
        
        if (idx + 1) % 5000 == 0:
            print(f"   - Processed {idx+1:,} / {len(msgs):,} messages... (Found {saved_count} items so far)")
            
    archive_past_events()
    print(f"✅ Ingestion complete for {json_filename}. Added/Updated {saved_count} items.")
    return saved_count

def main():
    init_db()
    ingest_from_json("result 2.json")

if __name__ == "__main__":
    main()
