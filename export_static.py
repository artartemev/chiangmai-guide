import sqlite3
import json
import os
from datetime import datetime
import curation

def export():
    conn = sqlite3.connect('chiangmai_guide.db')
    curation.apply(conn)  # manual edits from the local admin always win
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Fetch all items
    cursor.execute("SELECT * FROM items WHERE COALESCE(status, 'active') = 'active' ORDER BY id ASC")
    raw_items = [dict(r) for r in cursor.fetchall()]
    
    items = []
    items_map = {}
    reviews_map = {}
    today = datetime.now().strftime("%Y-%m-%d")
    
    for d in raw_items:
        item_id = d["id"]
        photos = []
        is_real_photo = False
        
        # Parse photos_json
        if d.get("photos_json"):
            try:
                p_list = json.loads(d["photos_json"])
                if isinstance(p_list, list) and len(p_list) > 0:
                    photos = p_list
                    is_real_photo = True
            except:
                pass
                
        # Fallback local place photo
        if not photos:
            if os.path.exists(f"static/photos/places/{item_id}.jpg"):
                photos = [f"static/photos/places/{item_id}.jpg"]
                is_real_photo = True
                
        # Telegram channel photo fallback
        if not photos:
            cursor.execute("SELECT telegram_msg_id, channel_username FROM reviews WHERE item_id = ?", (item_id,))
            for mid, ch in cursor.fetchall():
                if ch in ("@ChiamgMaimy", "Мой Чиангмай") or d.get("category") == "event":
                    mid_str = str(mid)
                    if '_' in mid_str:
                        parts = mid_str.split('_')
                        if parts[0].isdigit() and parts[1].isdigit():
                            calc_id = int(parts[0]) + int(parts[1]) - 1
                            if os.path.exists(f"static/photos/{calc_id}.jpg"):
                                photos = [f"static/photos/{calc_id}.jpg"]
                                is_real_photo = True
                                break
                    base_id = mid_str.split('_')[0]
                    if os.path.exists(f"static/photos/{base_id}.jpg"):
                        photos = [f"static/photos/{base_id}.jpg"]
                        is_real_photo = True
                        break
                    if base_id.isdigit():
                        bid = int(base_id)
                        for candidate in (bid - 1, bid + 1, bid - 2):
                            if os.path.exists(f"static/photos/{candidate}.jpg"):
                                photos = [f"static/photos/{candidate}.jpg"]
                                is_real_photo = True
                                break
                    if photos:
                        break
                        
        # Ensure paths are clean relative paths without leading slash
        clean_photos = []
        for p in photos:
            if p.startswith('/'):
                p = p[1:]
            clean_photos.append(p)
            
        d["photos"] = clean_photos
        d["is_real_photo"] = is_real_photo
        
        # Parse community_summary
        if d.get("community_summary") and isinstance(d["community_summary"], str):
            try:
                d["community_summary"] = json.loads(d["community_summary"])
            except:
                d["community_summary"] = {}
        elif not d.get("community_summary"):
            d["community_summary"] = {}
            
        # Fetch reviews for modal
        cursor.execute("SELECT review_text, sender_name, msg_date, source_link FROM reviews WHERE item_id = ? ORDER BY id DESC", (item_id,))
        reviews_map[item_id] = [dict(r) for r in cursor.fetchall()]
        d["review_count"] = len(reviews_map[item_id])
        d["veg_friendly"] = bool(d.get("veg_friendly"))
        d.pop("photos_json", None)
        d.pop("status", None)
        try:
            d["tags"] = json.loads(d.get("tags") or "[]")
        except Exception:
            d["tags"] = []
        oh = d.get("opening_hours")
        if isinstance(oh, str) and oh.startswith("{"):
            try:
                d["opening_hours"] = json.loads(oh)
            except Exception:
                d["opening_hours"] = None
        elif not oh:
            d["opening_hours"] = None
        if d["category"] == "event":
            iso = d.get("event_iso_date")
            d["is_active"] = (not iso) or iso >= today
        
        items.append(d)
        items_map[item_id] = d
        
    # 2. Fetch collections
    cursor.execute("SELECT * FROM collections ORDER BY id ASC")
    collections = [dict(r) for r in cursor.fetchall()]
    
    for col in collections:
        col_id = col["id"]
        cursor.execute("""
            SELECT i.id, ci.note 
            FROM items i 
            JOIN collection_items ci ON i.id = ci.item_id 
            WHERE ci.collection_id = ? 
            ORDER BY ci.sort_order ASC
        """, (col_id,))
        col["items"] = [{"id": r["id"], "note": r["note"]} for r in cursor.fetchall()]
        
    # 3. Compute stats
    cursor.execute("SELECT category, count(*) FROM items WHERE COALESCE(status,'active')='active' GROUP BY category")
    cats = dict(cursor.fetchall())
    cursor.execute("SELECT neighborhood, count(*) FROM items WHERE neighborhood != 'Other' GROUP BY neighborhood")
    neighs = dict(cursor.fetchall())
    cursor.execute("SELECT count(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM items WHERE category='event' AND (event_iso_date IS NULL OR event_iso_date >= ?)", (today,))
    active_events = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM items WHERE category='event' AND event_iso_date IS NOT NULL AND event_iso_date < ?", (today,))
    past_events = cursor.fetchone()[0]
    
    stats = {
        "categories": cats,
        "neighborhoods": neighs,
        "total_reviews": total_reviews,
        "active_events": active_events,
        "past_events": past_events,
        "total_items": len(items)
    }
    
    conn.close()
    
    data = {
        "generated_at": datetime.now().isoformat(),
        "stats": stats,
        "collections": collections,
        "items": items
    }
    
    out_path = "static/data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=None) # compact json
        
    with open("static/reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews_map, f, ensure_ascii=False, indent=None)

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Exported static data to {out_path} ({size_mb:.2f} MB, {len(items)} items, {len(collections)} routes)")

if __name__ == "__main__":
    export()
