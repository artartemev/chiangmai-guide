from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import json
import re
from datetime import datetime
from database import get_db

from typing import Optional

os.makedirs("static/photos", exist_ok=True)

app = FastAPI(title="Chiang Mai Field Guide (TE x Zen Edition)")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/items")
def get_items(
    category: Optional[str] = None,
    dietary: Optional[str] = None,
    neighborhood: Optional[str] = None,
    event_status: Optional[str] = None,
    has_maps: bool = False,
    veg_friendly: bool = False,
    min_mentions: int = 0,
    sort_by: str = "mentions",
    q: Optional[str] = None,
    current_date: Optional[str] = None,
    exclude_events: bool = False
):
    conn = get_db()
    cursor = conn.cursor()
    
    # Real-time dynamic date
    today = current_date or datetime.now().strftime("%Y-%m-%d")
    
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    
    if category and category != "all":
        if category == "nature":
            query += " AND category IN ('nature', 'hiking_trail')"
        else:
            query += " AND category = ?"
            params.append(category)
    elif exclude_events:
        query += " AND category != 'event'"
        
    if dietary and dietary != "all":
        query += " AND dietary_type = ?"
        params.append(dietary)
        
    if neighborhood and neighborhood != "all":
        query += " AND neighborhood = ?"
        params.append(neighborhood)
        
    # Dynamic date filtering for events
    if event_status == "past":
        query += " AND category = 'event' AND event_iso_date IS NOT NULL AND event_iso_date < ?"
        params.append(today)
    elif event_status == "active":
        query += " AND (category != 'event' OR (event_iso_date IS NULL OR event_iso_date >= ?))"
        params.append(today)
    elif event_status == "all":
        pass
    else:
        # Default: hide past events in all views
        query += " AND (category != 'event' OR (event_iso_date IS NULL OR event_iso_date >= ?))"
        params.append(today)

    if has_maps:
        query += " AND location_url != ''"
        
    if veg_friendly:
        query += " AND veg_friendly = 1"

    if min_mentions > 0:
        query += " AND mention_count >= ?"
        params.append(min_mentions)
        
    if q:
        q_lower = q.lower()
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(neighborhood) LIKE ? OR LOWER(venue_name) LIKE ?)"
        params.extend([f"%{q_lower}%", f"%{q_lower}%", f"%{q_lower}%", f"%{q_lower}%"])
        
    if sort_by == "newest":
        query += " ORDER BY updated_at DESC, mention_count DESC"
    elif sort_by == "alpha":
        query += " ORDER BY title ASC"
    elif category == "event":
        query += " ORDER BY (CASE WHEN event_iso_date IS NULL THEN '9999' ELSE event_iso_date END) ASC, mention_count DESC"
    else:
        query += " ORDER BY mention_count DESC, id DESC"
        
    cursor.execute(query, params)
    rows = []
    cursor2 = conn.cursor()
    
    for r in cursor.fetchall():
        d = dict(r)
        
        # Real photo resolution
        photos = []
        is_real_photo = False
        
        # 1. Stored explicit photos in photos_json
        if d.get("photos_json"):
            try:
                stored = json.loads(d["photos_json"])
                if stored and isinstance(stored, list):
                    valid = [p for p in stored if os.path.exists(p.lstrip('/'))]
                    if valid:
                        photos = valid
                        is_real_photo = True
            except Exception:
                pass

        # 2. Dedicated authentic place photo
        if not photos and os.path.exists(f"static/photos/places/{d['id']}.jpg"):
            photos = [f"/static/photos/places/{d['id']}.jpg"]
            is_real_photo = True
        
        
        # 3. Telegram channel afisha or photo (strictly from @ChiamgMaimy or events)
        if not photos:
            cursor2.execute("SELECT telegram_msg_id, channel_username FROM reviews WHERE item_id = ?", (d["id"],))
            for mid, ch in cursor2.fetchall():
                if ch in ("@ChiamgMaimy", "Мой Чиангмай") or d.get("category") == "event":
                    mid_str = str(mid)
                    if '_' in mid_str:
                        parts = mid_str.split('_')
                        if parts[0].isdigit() and parts[1].isdigit():
                            calc_id = int(parts[0]) + int(parts[1]) - 1
                            if os.path.exists(f"static/photos/{calc_id}.jpg"):
                                photos = [f"/static/photos/{calc_id}.jpg"]
                                is_real_photo = True
                                break
                    base_id = mid_str.split('_')[0]
                    if os.path.exists(f"static/photos/{base_id}.jpg"):
                        photos = [f"/static/photos/{base_id}.jpg"]
                        is_real_photo = True
                        break
                    if base_id.isdigit():
                        bid = int(base_id)
                        for candidate in (bid - 1, bid + 1, bid - 2):
                            if os.path.exists(f"static/photos/{candidate}.jpg"):
                                photos = [f"/static/photos/{candidate}.jpg"]
                                is_real_photo = True
                                break
                    if photos:
                        break
                
        d["photos"] = photos
        d["is_real_photo"] = is_real_photo

        if d.get("community_summary") and isinstance(d["community_summary"], str):
            try:
                d["community_summary"] = json.loads(d["community_summary"])
            except Exception:
                pass

        if d.get("category") == "event":
            iso = d.get("event_iso_date")
            d["is_active"] = (iso is None or iso >= today)
            d["dynamic_status"] = "active" if d["is_active"] else "past"
        rows.append(d)
        
    conn.close()
    return rows

def clean_snippet(text: str) -> str:
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def truncate_clean(s: str, max_len: int = 150) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len].rsplit(' ', 1)[0] + '…'

CHAT_NOISE = [
    'подскажите', 'подскажи', 'кто знает', 'кто-то', 'есть ли', 'а сюда вообще',
    'ага понял', 'пардон', 'пишите в личку', 'приглашаем', 'приглашаю',
    'на своих байках', 'как пассажир', 'встречаемся', 'выезжаем', 'по домам',
    'составили маршрут', 'на одну ночь', 'всем привет', 'привет всем',
    'ребята', 'ребят', 'кто со мной', 'кто поедет', 'возьмите меня', 'скиньте',
    'посоветуйте', 'влезаю', 'перевод от жпт', 'полина кидала',
    'хер знает', 'чет типа', 'блин', 'че бы нет', 'не имеет смысла',
    'подборка по', 'часть 1', 'часть 2', 'часть 3', 'в личку', 'отзовитесь',
    'кто был', 'кто-нибудь', 'как думаете', 'не знаете', 'в идеале на рассвете'
]

def synthesize_reviews(title: str, category: str, desc: str, reviews: list) -> dict:
    clean_texts = []
    for r in reviews:
        t = clean_snippet(r.get('review_text', '') if isinstance(r, dict) else str(r))
        if len(t.split()) >= 4:
            clean_texts.append(t)
            
    price_signals = []
    tip_signals = []
    highlight_signals = []
    
    price_keywords = ['бат', 'thb', 'руб', 'вход', 'цена', 'билет', 'бесплатно', 'free', 'дорого', 'дешево', 'чек', 'донейшен', 'платн']
    tip_keywords = ['дорога', 'байк', 'парковк', 'закат', 'рассвет', 'утром', 'вечером', 'сезон', 'подъем', 'обувь', 'пешком', 'вода', 'осторожно', 'время', 'часы', 'бронь', 'маршрут', 'тропа', 'серпантин', 'жар', 'наличны']
    
    for t in clean_texts:
        sentences = re.split(r'[.!?\n]+', t)
        for s in sentences:
            s = s.strip(' -•–\t\r')
            if len(s.split()) < 4 or len(s) < 18 or len(s) > 160:
                continue
            if '?' in s or any(n in s.lower() for n in CHAT_NOISE):
                continue
            if re.match(r'^\d+[\.\)]', s):
                continue
            if s.count(',') > 5 or s.count(' - ') > 2:
                continue
            s_lower = s.lower()
            if any(k in s_lower for k in price_keywords) and not any(p in s for p in price_signals):
                price_signals.append(truncate_clean(s, 160))
            elif any(k in s_lower for k in tip_keywords) and not any(p in s for p in tip_signals):
                tip_signals.append(truncate_clean(s, 160))
            elif len(s) >= 20 and not any(p in s for p in highlight_signals):
                highlight_signals.append(truncate_clean(s, 160))
                
    if not highlight_signals and desc:
        first_desc = desc.split('.')[0].strip()
        if len(first_desc) > 20 and not any(n in first_desc.lower() for n in CHAT_NOISE):
            highlight_signals.append(truncate_clean(first_desc, 160))
            
    if not highlight_signals:
        highlight_signals.append("Популярная локация Чиангмая, проверенная участниками сообщества.")
            
    return {
        'highlights': highlight_signals[:2],
        'pricing': price_signals[:2],
        'tips': tip_signals[:2],
        'count': len(reviews)
    }

@app.get("/api/item/{item_id}")
def get_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item_row = cursor.fetchone()
    if not item_row:
        conn.close()
        return JSONResponse({"error": "Not found"}, status_code=404)
        
    item = dict(item_row)
    
    # Real photo resolution
    photos = []
    is_real_photo = False
    
    # 1. Stored explicit photos in photos_json
    if item.get("photos_json"):
        try:
            stored = json.loads(item["photos_json"])
            if stored and isinstance(stored, list):
                valid = [p for p in stored if os.path.exists(p.lstrip('/'))]
                if valid:
                    photos = valid
                    is_real_photo = True
        except Exception:
            pass

    # 2. Dedicated authentic place photo
    if not photos and os.path.exists(f"static/photos/places/{item_id}.jpg"):
        photos = [f"/static/photos/places/{item_id}.jpg"]
        is_real_photo = True
    

    # 3. Telegram message photo / poster
    if not photos:
        cursor.execute("SELECT telegram_msg_id, channel_username FROM reviews WHERE item_id = ?", (item_id,))
        for mid, ch in cursor.fetchall():
            if ch in ("@ChiamgMaimy", "Мой Чиангмай") or item.get("category") == "event":
                mid_str = str(mid)
                if '_' in mid_str:
                    parts = mid_str.split('_')
                    if parts[0].isdigit() and parts[1].isdigit():
                        calc_id = int(parts[0]) + int(parts[1]) - 1
                        if os.path.exists(f"static/photos/{calc_id}.jpg"):
                            photos = [f"/static/photos/{calc_id}.jpg"]
                            is_real_photo = True
                            break
                base_id = mid_str.split('_')[0]
                if os.path.exists(f"static/photos/{base_id}.jpg"):
                    photos = [f"/static/photos/{base_id}.jpg"]
                    is_real_photo = True
                    break
                if base_id.isdigit():
                    bid = int(base_id)
                    for candidate in (bid - 1, bid + 1, bid - 2):
                        if os.path.exists(f"static/photos/{candidate}.jpg"):
                            photos = [f"/static/photos/{candidate}.jpg"]
                            is_real_photo = True
                            break
                if photos:
                    break
            
    item["photos"] = photos
    item["is_real_photo"] = is_real_photo

    cursor.execute("SELECT * FROM reviews WHERE item_id = ? ORDER BY id DESC", (item_id,))
    reviews = [dict(r) for r in cursor.fetchall()]
    item["reviews"] = reviews

    # Use curated summary if stored in database
    if item.get("community_summary"):
        try:
            item["community_summary"] = json.loads(item["community_summary"])
        except Exception:
            item["community_summary"] = synthesize_reviews(
                item.get("title") or "",
                item.get("category") or "",
                item.get("description") or "",
                reviews
            )
    else:
        item["community_summary"] = synthesize_reviews(
            item.get("title") or "",
            item.get("category") or "",
            item.get("description") or "",
            reviews
        )
    conn.close()
    return item

@app.get("/api/stats")
def get_stats(current_date: Optional[str] = None):
    today = current_date or datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT category, count(*) FROM items GROUP BY category")
    cats = dict(cursor.fetchall())
    cursor.execute("SELECT neighborhood, count(*) FROM items WHERE neighborhood != 'Other' GROUP BY neighborhood")
    neighs = dict(cursor.fetchall())
    cursor.execute("SELECT count(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM items WHERE category='event' AND (event_iso_date IS NULL OR event_iso_date >= ?)", (today,))
    active_events = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM items WHERE category='event' AND event_iso_date IS NOT NULL AND event_iso_date < ?", (today,))
    past_events = cursor.fetchone()[0]
    
    conn.close()
    return {
        "categories": cats,
        "neighborhoods": neighs,
        "total_reviews": total_reviews,
        "active_events": active_events,
        "past_events": past_events,
        "current_date": today
    }




@app.get("/api/collections")
def get_collections():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM collections ORDER BY id ASC")
    cols = [dict(row) for row in c.fetchall()]
    conn.close()
    return cols

@app.get("/api/collections/{collection_id}")
def get_collection(collection_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM collections WHERE id = ?", (collection_id,))
    col_row = c.fetchone()
    if not col_row:
        conn.close()
        return JSONResponse({"error": "not found"}, status_code=404)
        
    c.execute("""
        SELECT i.*, ci.note 
        FROM items i 
        JOIN collection_items ci ON i.id = ci.item_id 
        WHERE ci.collection_id = ? 
        ORDER BY ci.sort_order ASC
    """, (collection_id,))
    items = []
    cursor2 = conn.cursor()
    for r in c.fetchall():
        d = dict(r)
        # We need the same photo logic as in get_items
        photos = []
        is_real_photo = False
        import os, json
        
        if d.get("photos_json"):
            try:
                stored = json.loads(d["photos_json"])
                if stored and isinstance(stored, list):
                    valid = [p for p in stored if os.path.exists(p.lstrip('/'))]
                    if valid:
                        photos = valid
                        is_real_photo = True
            except: pass
            
            if not photos and os.path.exists(f"static/photos/places/{d['id']}.jpg"):
                photos = [f"/static/photos/places/{d['id']}.jpg"]
                is_real_photo = True
            
        
            
        if not photos:
            cursor2.execute("SELECT telegram_msg_id, channel_username FROM reviews WHERE item_id = ?", (d["id"],))
            for mid, ch in cursor2.fetchall():
                if ch in ("@ChiamgMaimy", "Мой Чиангмай") or d.get("category") == "event":
                    mid_str = str(mid)
                    if '_' in mid_str:
                        parts = mid_str.split('_')
                        if parts[0].isdigit() and parts[1].isdigit():
                            calc_id = int(parts[0]) + int(parts[1]) - 1
                            if os.path.exists(f"static/photos/{calc_id}.jpg"):
                                photos = [f"/static/photos/{calc_id}.jpg"]
                                is_real_photo = True
                                break
                    base_id = mid_str.split('_')[0]
                    if os.path.exists(f"static/photos/{base_id}.jpg"):
                        photos = [f"/static/photos/{base_id}.jpg"]
                        is_real_photo = True
                        break
                    if base_id.isdigit():
                        bid = int(base_id)
                        for candidate in (bid - 1, bid + 1, bid - 2):
                            if os.path.exists(f"static/photos/{candidate}.jpg"):
                                photos = [f"/static/photos/{candidate}.jpg"]
                                is_real_photo = True
                                break
                    if photos: break
                    
        d["photos"] = photos
        d["is_real_photo"] = is_real_photo
        if d.get("community_summary") and isinstance(d["community_summary"], str):
            try: d["community_summary"] = json.loads(d["community_summary"])
            except: pass
        items.append(d)
        
    conn.close()
    result = dict(col_row)
    result["items"] = items
    return result

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
