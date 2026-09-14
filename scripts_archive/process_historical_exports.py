import json
import os
import re
import sys
from database import init_db, get_db
from llm_extractor import extract_with_rules
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

def process_file(json_name):
    fpath = os.path.join(PARENT_DIR, json_name)
    if not os.path.exists(fpath):
        print(f"⚠️ File {json_name} not found.")
        return
        
    print(f"\n📖 Reading {json_name}...")
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    chat_name = data.get("name", json_name)
    chat_username = ""
    msgs = data.get("messages", [])
    print(f"💬 Loaded {len(msgs):,} messages from \"{chat_name}\"")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT msg_id FROM processed_messages")
    processed_ids = set(r[0] for r in cursor.fetchall())
    conn.close()
    
    saved_items = 0
    processed_count = 0
    
    for idx, m in enumerate(msgs):
        m_id = m.get("id")
        if not m_id or m_id in processed_ids:
            continue
            
        raw_text = extract_text(m.get("text", "")).strip()
        if not raw_text or len(raw_text) < 12:
            continue
            
        # Check if message contains maps link or place/event/trail keywords
        extracted = extract_with_rules(raw_text)
        if extracted and extracted.get("has_entity"):
            sender = m.get("from") or m.get("actor") or "Система"
            msg_date = m.get("date", "").replace("T", " ")
            
            review_meta = {
                "msg_id": m_id,
                "channel": chat_name,
                "sender": sender,
                "date": msg_date,
                "text": raw_text,
                "reactions": "",
                "source_link": f"https://t.me/c/{data.get('id')}/{m_id}" if data.get('id') else ""
            }
            
            saved_id = process_and_save_entity(extracted, review_meta)
            if saved_id:
                saved_items += 1
                
        processed_count += 1
        processed_ids.add(m_id)
        
        if (idx + 1) % 10000 == 0:
            print(f"   - Progress: {idx+1:,} / {len(msgs):,} messages... (Extracted {saved_items:,} places/trails/events so far)")
            
    print(f"✅ Finished {json_name}! Processed {processed_count:,} messages, added/updated {saved_items:,} items in DB.")

def main():
    init_db()
    print("🚀 Starting Batch Processing of Historical Exports (result 3.json, result 4.json, result 5.json)...")
    for fname in ["result 3.json", "result 4.json", "result 5.json"]:
        process_file(fname)
    archive_past_events()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM items")
    total_items = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]
    conn.close()
    print(f"\n🎉 HISTORICAL BACKFILL COMPLETE!")
    print(f"📊 Total Places & Events in Database: {total_items:,}")
    print(f"💬 Total User Recommendations & Mentions: {total_reviews:,}")

if __name__ == "__main__":
    main()
