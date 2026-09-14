import json
import re
from datetime import datetime
from database import get_db

VISA_AND_NOISE_KEYWORDS = [
    "yellow-tabien-baan", "tabien baan", "табиен баан", "желтая книга", "жёлтая книга",
    "thaicitizenship", "citizenship", "гражданство",
    "dtv", "tourist visa", "student visa", "elite visa", "retirement visa", "виза", "визовый", "визовые",
    "бордер рам", "бордерран", "border run", "visa run", "иммиграци", "immigration", "tm30", "tm6", "tm.30",
    "work permit", "разрешение на работу",
    "resident certificate", "справка о резиденти", "сертификат резидентства",
    "driver license", "driving license", "водительские права", "права на байк", "права в таиланде",
    "открыть счет", "счет в банке", "карта банкомата", "открытие счета",
    "штамп", "консульство", "посольство", "паспорт", "загранпаспорт",
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "аренда кондо", "за последние сутки", "в чате обсуждали:", "daily digest"
]

GENERIC_TITLES = [
    "всем привет", "всем привет!", "добрый день", "здравствуйте", "здравствуйте!", "добрый вечер",
    "ребят, привет", "привет всем", "доброе утро", "локация", "интересное место", "вот такой",
    "вот здесь хорошо", "это да", "я нашла)", "спасибо", "отлично!)", "координаты", "точка на карте",
    "сегодня пятница", "я ищу магазины", "планируем приезд", "поделитесь контактами", "кто знает",
    "подскажите пожалуйста", "доброе утро друзья", "привет", "приветствую", "информация",
    "заведение chiang mai", "интересное место", "локация"
]

def normalize_name(name):
    return re.sub(r"[^\w\s]", "", name.lower()).strip()

def process_and_save_entity(entity, review_meta):
    if not entity.get("has_entity"): 
        return None
        
    title = entity.get("title", "").strip()
    norm_title = normalize_name(title)
    rev_text = review_meta.get("text", "").lower()
    
    # 1. Visa, document, legal guide rejection
    if any(k in rev_text for k in VISA_AND_NOISE_KEYWORDS) or any(k in norm_title for k in VISA_AND_NOISE_KEYWORDS):
        return None
        
    # 2. Reject generic title without verified venue name
    if not title or norm_title in GENERIC_TITLES or len(norm_title) < 2:
        return None
    
    category = entity.get("category", "cafe_restaurant")
    dietary = entity.get("dietary_type", "none")
    neighborhood = entity.get("neighborhood", "Other")
    desc = entity.get("description", "")
    loc_url = entity.get("location_url", "")
    evt_date = entity.get("event_date", "")
    
    evt_status = "none"
    if category == "event":
        today_str = datetime.now().strftime("%Y-%m-%d")
        if evt_date and evt_date < today_str:
            evt_status = "archived"
        else:
            evt_status = "upcoming"
            
    now_str = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    
    target_id = None
    
    # Match existing strictly by canonical location_url or exact normalized venue name within category
    if loc_url:
        cursor.execute("SELECT id FROM items WHERE location_url = ?", (loc_url,))
        row = cursor.fetchone()
        if row:
            target_id = row["id"]
            
    if not target_id and len(norm_title) > 3:
        cursor.execute("SELECT id, title FROM items WHERE category = ?", (category,))
        rows = cursor.fetchall()
        for row in rows:
            r_norm = normalize_name(row["title"])
            if r_norm == norm_title:
                target_id = row["id"]
                break
            
    if target_id:
        # Existing item -> Update and Enrich
        cursor.execute("""
            UPDATE items 
            SET mention_count = mention_count + 1,
                updated_at = ?,
                location_url = CASE WHEN location_url = "" THEN ? ELSE location_url END,
                dietary_type = CASE WHEN dietary_type = "none" THEN ? ELSE dietary_type END
            WHERE id = ?
        """, (now_str, loc_url, dietary, target_id))
    else:
        # New item -> Insert
        cursor.execute("""
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, event_date, event_status, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (title, category, dietary, neighborhood, desc, loc_url, evt_date, evt_status, now_str, now_str))
        target_id = cursor.lastrowid
        
    # Save review record
    cursor.execute("""
        INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        target_id,
        review_meta.get("msg_id"),
        review_meta.get("channel"),
        review_meta.get("sender"),
        review_meta.get("date"),
        review_meta.get("text"),
        review_meta.get("reactions"),
        review_meta.get("source_link")
    ))
    
    conn.commit()
    conn.close()
    return target_id

def archive_past_events():
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items 
        SET event_status = "archived" 
        WHERE category = "event" 
          AND event_status = "upcoming" 
          AND event_date != "" 
          AND event_date < ?
    """, (today_str,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    archive_past_events()
    print("Deduplicator module ready with strict quality rules.")
