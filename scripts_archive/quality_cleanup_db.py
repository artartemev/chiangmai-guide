import sqlite3
import re
import urllib.parse
from datetime import datetime

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"

VISA_AND_NOISE_KEYWORDS = [
    # Visa & documents
    "yellow-tabien-baan", "tabien baan", "табиен баан", "желтая книга", "жёлтая книга",
    "thaicitizenship", "citizenship", "гражданство",
    "dtv", "tourist visa", "student visa", "elite visa", "retirement visa", "виза", "визовый", "визовые",
    "бордер рам", "бордерран", "border run", "visa run", "иммиграци", "immigration", "tm30", "tm6", "tm.30",
    "work permit", "разрешение на работу",
    "resident certificate", "справка о резиденти", "сертификат резидентства",
    "driver license", "driving license", "водительские права", "права на байк", "права в таиланде",
    "открыть счет", "счет в банке", "карта банкомата", "открытие счета",
    "штамп", "консульство", "посольство", "паспорт", "загранпаспорт",
    # Rentals & Digests & Housing & General Questions
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "аренда кондо", "за последние сутки", "в чате обсуждали:", "daily digest",
    "кто может", "кто знае", "подскажите", "где лучше", "как добраться"
]

GENERIC_TITLES = [
    "всем привет", "всем привет!", "добрый день", "здравствуйте", "здравствуйте!", "добрый вечер",
    "ребят, привет", "привет всем", "доброе утро", "локация", "интересное место", "вот такой",
    "вот здесь хорошо", "это да", "я нашла)", "спасибо", "отлично!)", "координаты", "точка на карте",
    "сегодня пятница", "я ищу магазины", "планируем приезд", "поделитесь контактами", "кто знает",
    "подскажите пожалуйста", "доброе утро друзья", "привет", "приветствую", "информация",
    "заведение chiang mai", "интересное место", "локация", "здесь", "тут", "вот", "1.", "2.", "3."
]

VERB_SNIPPETS = ["собираемся", "советую", "пишет", "ведет", "ведет)", "нынче", "потреккить", "присоединился", "запрыгнули", "стартуем"]

NEIGHBORHOODS = ["Nimman", "Old City", "Hang Dong", "Mae Rim", "Mae On", "San Sai", "Santitham", "Chang Phueak", "Jed Yod", "Doi Suthep", "Mae Kampong"]

def normalize_name(name):
    return re.sub(r"[^\w\s]", "", name.lower()).strip()

def extract_canonical_url(text):
    maps_match = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", text)
    if maps_match:
        url = maps_match.group(0).rstrip(".,)")
        url = re.sub(r"([?&])g_st=[^&]+", "", url).rstrip("?&")
        return url
    alltrails_match = re.search(r"https?://[\w\.-]*alltrails\.com/trail/[^\s,\)\"\']*", text)
    if alltrails_match:
        return alltrails_match.group(0).rstrip(".,)")
    return ""

def extract_clean_title(txt, loc_url):
    if not txt:
        return None

    # 1. 📍 Location pin marker
    pin_match = re.search(r"📍\s*([^\n\r,\.\?]+)", txt)
    if pin_match:
        cand = pin_match.group(1).strip()
        cand = re.sub(r"#\w+", "", cand).strip()
        cand = re.sub(r"https?://\S+", "", cand).strip()
        if len(cand) >= 3 and not cand.lower().startswith("http") and cand.lower() not in GENERIC_TITLES:
            return cand

    # 2. AllTrails URL slug
    if "alltrails.com" in loc_url:
        at_match = re.search(r"alltrails\.com/trail/[^/\s]+/[^/\s]+/([a-z0-9-]+)", loc_url)
        if at_match:
            return at_match.group(1).replace("-", " ").title()

    # 3. Google Maps query parameter
    if loc_url:
        q_match = re.search(r"[?&]q=([^&\s]+)", loc_url)
        if q_match:
            val = urllib.parse.unquote(q_match.group(1)).replace("+", " ").strip()
            if val and not val.replace(".", "").isdigit() and len(val) > 2 and val.lower() not in GENERIC_TITLES:
                return val

    # 4. Text with dash separator e.g. "Sanpakoi Street Market — небольшой рынок"
    dash_match = re.search(r"^([A-Z0-9\s\'&\.-]{3,45})\s*[—–-]\s*", txt.strip(), re.MULTILINE)
    if dash_match:
        cand = dash_match.group(1).strip()
        if len(cand) >= 3 and cand.lower() not in GENERIC_TITLES:
            return cand

    # 5. English / Thai venue name inside lines
    eng_match = re.search(r"\b([A-Z][a-zA-Z0-9\s\'&]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|Bakery|Bar|Trail|Waterfall|Coworking|Hub|House|Villa|Hotel|Retreat|Farm))\b", txt)
    if eng_match:
        cand = eng_match.group(1).strip()
        if cand.lower() not in GENERIC_TITLES:
            return cand

    # 6. Russian quoted name e.g. кафе "Имя"
    ru_quote = re.search(r'(?:кафе|ресторан|водопад|коворкинг|тропа|хайк|отель|бар)\s+["«]([^"»]+)["»]', txt, re.IGNORECASE)
    if ru_quote:
        return ru_quote.group(1).strip()

    # 7. First line if short clean proper title
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    if lines:
        first = lines[0]
        cleaned = re.sub(r"^[^\w\s]+", "", first).strip()
        cleaned = re.sub(r"^\[.*?\]\s*", "", cleaned).strip()
        cleaned = re.sub(r"#\w+", "", cleaned).strip()
        
        lower_c = cleaned.lower()
        if (len(cleaned) >= 3 and len(cleaned) <= 45 
            and not any(g in lower_c for g in ["всем привет", "добрый день", "здравствуйте", "привет", "подскажите", "кто знает", "где ", "как ", "спасибо", "подсказать", "ребята", "пожалуйста", "ищу ", "мы ", "вы ", "кто ", "если ", "рекомендую", "отличный"])
            and not any(v in lower_c for v in VERB_SNIPPETS)
            and not cleaned.startswith("http")
            and not cleaned.startswith("www")
            and not cleaned.startswith("1.")
            and not cleaned.startswith("2.")):
            return cleaned

    return None

def determine_category(txt):
    lower = txt.lower()
    if any(k in lower for k in ["коворкинг", "coworking", "рабоч space", "hub", "yellow coworking", "punspace", "camp maya"]):
        return "workspace"
    elif any(k in lower for k in ["водопад", "waterfall", "каньон", "слоны", "слон", "озеро", "гора", "nature", "дои интанон", "viewpoint", "нац парк", "national park"]):
        return "nature"
    elif any(k in lower for k in ["хайк", "хайкинг", "трек", "тропа", "trail", "hike", "hiking", "monk trail", "треккинг"]):
        return "hiking_trail"
    elif any(k in lower for k in ["митап", "ивент", "фестиваль", "концерт", "вечеринка", "event", "meetup", "party", "воркшоп", "workshop"]):
        return "event"
    return "cafe_restaurant"

def determine_dietary(txt):
    lower = txt.lower()
    if "веган" in lower or "vegan" in lower:
        return "vegan"
    elif "вегетариан" in lower or "vegetarian" in lower:
        return "vegetarian"
    elif "кофе" in lower or "coffee" in lower or "кофейн" in lower or "matcha" in lower:
        return "coffee_only"
    return "omnivore"

def determine_neighborhood(txt):
    lower = txt.lower()
    for n in NEIGHBORHOODS:
        if n.lower() in lower:
            return n
    return "Other"

def run_cleanup():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reviews")
    all_reviews = cursor.fetchall()
    print(f"Loaded {len(all_reviews)} total reviews from database.")

    valid_records = []
    filtered_visa_count = 0
    filtered_no_title_count = 0

    for r in all_reviews:
        txt = r["review_text"] or ""
        txt_lower = txt.lower()

        # 1. Visa & Noise filter
        if any(k in txt_lower for k in VISA_AND_NOISE_KEYWORDS):
            filtered_visa_count += 1
            continue

        loc_url = extract_canonical_url(txt)
        title = extract_clean_title(txt, loc_url)

        # 2. Strict rejection if no specific venue title extracted
        if not title or normalize_name(title) in GENERIC_TITLES:
            filtered_no_title_count += 1
            continue

        category = determine_category(txt)
        dietary = determine_dietary(txt)
        neighborhood = determine_neighborhood(txt)

        valid_records.append({
            "review": r,
            "title": title,
            "category": category,
            "dietary_type": dietary,
            "neighborhood": neighborhood,
            "location_url": loc_url,
            "text": txt
        })

    print(f"Filtered out visa/document/rental/digest/question reviews: {filtered_visa_count}")
    print(f"Filtered out reviews without specific venue title: {filtered_no_title_count}")
    print(f"Total verified venue recommendations: {len(valid_records)}")

    # Deduplication & Aggregation
    grouped_items = {}

    for rec in valid_records:
        loc_url = rec["location_url"]
        title = rec["title"]
        norm_t = normalize_name(title)

        if loc_url:
            group_key = f"URL:{loc_url}"
        elif norm_t and len(norm_t) > 2:
            group_key = f"TITLE:{rec['category']}:{norm_t}"
        else:
            group_key = f"REV:{rec['review']['id']}"

        if group_key not in grouped_items:
            grouped_items[group_key] = {
                "title": title,
                "category": rec["category"],
                "dietary_type": rec["dietary_type"],
                "neighborhood": rec["neighborhood"],
                "description": rec["text"][:300].strip(),
                "location_url": loc_url,
                "reviews": [rec["review"]]
            }
        else:
            g = grouped_items[group_key]
            g["reviews"].append(rec["review"])
            if len(title) > len(g["title"]) and title.lower() not in GENERIC_TITLES:
                g["title"] = title
            if g["location_url"] == "" and loc_url:
                g["location_url"] = loc_url
            if g["dietary_type"] == "none" and rec["dietary_type"] != "none":
                g["dietary_type"] = rec["dietary_type"]
            if g["neighborhood"] == "Other" and rec["neighborhood"] != "Other":
                g["neighborhood"] = rec["neighborhood"]

    print(f"Deduplicated into {len(grouped_items)} high-quality catalog entities.")

    # Re-build database
    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('items', 'reviews')")

    now_str = datetime.now().isoformat()
    inserted_items_count = 0
    inserted_reviews_count = 0

    for key, item in grouped_items.items():
        mention_count = len(item["reviews"])
        cursor.execute("""
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, event_date, event_status, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, '', 'none', ?, ?, ?)
        """, (
            item["title"],
            item["category"],
            item["dietary_type"],
            item["neighborhood"],
            item["description"],
            item["location_url"],
            mention_count,
            now_str,
            now_str
        ))
        item_id = cursor.lastrowid
        inserted_items_count += 1

        for r in item["reviews"]:
            cursor.execute("""
                INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                r["telegram_msg_id"],
                r["channel_username"],
                r["sender_name"],
                r["msg_date"],
                r["review_text"],
                r["reactions_text"],
                r["source_link"]
            ))
            inserted_reviews_count += 1

    conn.commit()
    conn.close()
    print(f"Quality cleanup complete! Database updated with {inserted_items_count} clean items and {inserted_reviews_count} linked reviews.")

if __name__ == "__main__":
    run_cleanup()
