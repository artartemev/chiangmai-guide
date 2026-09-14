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
    # Rentals & Digests & Housing
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "аренда кондо", "за последние сутки", "в чате обсуждали:", "daily digest"
]

CHAT_QUESTION_PREFIXES = [
    "так,", "так ", "то есть", "предлагаю", "кто-то", "кто то", "вопрос", "кстати", "ребята", "друзья",
    "нашел", "ищу ", "подскажите", "знает", "завтра", "сегодня", "думаю", "хочу", "рекомендую", "всем привет",
    "добрый день", "здравствуйте", "привет", "пожалуйста", "какие ", "как ", "где ", "почему ", "если ",
    "были ", "кто ", "мы ", "вы ", "советую", "планируем", "собираемся", "поделитесь", "опыт ", "а кто",
    "а насколько", "какой ", "какая ", "какие ", "есть у кого", "подсказать", "может это", "и получается",
    "встречаемся", "стартуем", "точка сбора", "тропа протяженностью", "alltrails"
]

GENERIC_TITLES = [
    "всем привет", "всем привет!", "добрый день", "здравствуйте", "здравствуйте!", "добрый вечер",
    "ребят, привет", "привет всем", "доброе утро", "локация", "интересное место", "вот такой",
    "вот здесь хорошо", "это да", "я нашла)", "спасибо", "отлично!)", "координаты", "точка на карте",
    "сегодня пятница", "я ищу магазины", "планируем приезд", "поделитесь контактами", "кто знает",
    "подскажите пожалуйста", "доброе утро друзья", "привет", "приветствую", "информация",
    "заведение chiang mai", "интересное место", "локация", "здесь", "тут", "вот", "1.", "2.", "3.",
    "то есть фенси веган боул?", "так, предлагаю новую тему:", "точка сбора", "alltrails", "тропа протяженностью всего около 2"
]

NEIGHBORHOODS = ["Nimman", "Old City", "Hang Dong", "Mae Rim", "Mae On", "San Sai", "Santitham", "Chang Phueak", "Jed Yod", "Doi Suthep", "Mae Kampong"]

def normalize_name(name):
    return re.sub(r"[^\w\s]", "", name.lower()).strip()

def clean_title_prefix(cand):
    if not cand:
        return ""
    cand = re.sub(r"^(?:📍|Где:\s*|Где\s*:\s*|Локация:\s*)", "", cand, flags=re.IGNORECASE).strip()
    cand = re.sub(r"#\w+", "", cand).strip()
    cand = re.sub(r"https?://\S+", "", cand).strip()
    return cand

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

def extract_verified_proper_venue_name(txt, loc_url=""):
    if not txt:
        return None

    txt_strip = txt.strip()
    txt_lower = txt_strip.lower()

    if txt_strip.endswith("?") and not any(k in txt_lower for k in ["📍", "cafe", "restaurant", "bistro", "kitchen", "waterfall", "trail", "coworking", "водопад", "храм", "тропа"]):
        return None

    # 1. 📍 Location pin marker e.g. 📍 Vaanaa Cafe & Bistro
    pin_match = re.search(r"(?:📍|Где:\s*)\s*([^\n\r,\.\?]+)", txt, re.IGNORECASE)
    if pin_match:
        cand = clean_title_prefix(pin_match.group(1))
        if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", cand) and not re.search(r"^-+$", cand):
            return cand

    # 2. English / Thai Proper Venue Name e.g. Chai "N" Thai, Goodsouls Kitchen, Basecamp Trail Cafe, Yellow Coworking
    eng_quoted = re.search(r'\b([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|Bakery|Bar|Trail|Waterfall|Coworking|Hub|House|Villa|Hotel|Retreat|Farm|Baan|Thai|Tea|Tapas|Grill|Noodle|Pizza|Sushi|Vegan|Club|Phrasingh))\b', txt)
    if eng_quoted:
        cand = clean_title_prefix(eng_quoted.group(1))
        if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", cand) and not re.search(r"^-+$", cand):
            return cand

    # 3. Russian quoted venue name e.g. кафе "Дао", водопад "Буа Тонг"
    ru_quote = re.search(r'(?:кафе|ресторан|водопад|коворкинг|тропа|хайк|отель|бар|храм|рынок|парк)\s+["«]([^"»]+)["»]', txt, re.IGNORECASE)
    if ru_quote:
        cand = clean_title_prefix(ru_quote.group(1))
        if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", cand) and not re.search(r"^-+$", cand):
            return cand

    # 4. Russian venue declaration e.g. Водопад Буа Тонг, Храм Дой Сутеп, Озеро Хуай Туэнг Тао
    ru_decl = re.search(r'\b((?:Водопад|Храм|Гора|Озеро|Тропа|Кафе|Ресторан|Коворкинг|Парк)\s+[A-ZА-Яа-я0-9\s-]{3,30})\b', txt)
    if ru_decl:
        cand = clean_title_prefix(ru_decl.group(1))
        if len(cand) >= 4 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", cand) and not re.search(r"^-+$", cand) and not cand.lower().startswith("кафе правда"):
            return cand


    # 5. AllTrails URL slug e.g. alltrails.com/trail/thailand/chiang-mai/monk-s-trail -> Monk's Trail
    if "alltrails.com" in loc_url:
        at_match = re.search(r"alltrails\.com/trail/[^/\s]+/[^/\s]+/([a-z0-9-]+)", loc_url)
        if at_match:
            slug = clean_title_prefix(at_match.group(1).replace("-", " ").title())
            if slug.lower() not in GENERIC_TITLES:
                return slug

    # 6. Google Maps query param e.g. ?q=Superrich+Nimman -> Superrich Nimman
    if loc_url:
        q_match = re.search(r"[?&]q=([^&\s]+)", loc_url)
        if q_match:
            val = clean_title_prefix(urllib.parse.unquote(q_match.group(1)).replace("+", " "))
            if val and not val.replace(".", "").isdigit() and len(val) > 2 and not val.endswith("?") and not any(val.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", val):
                return val

    # 7. Text with dash separator starting with Proper Case English Name e.g. "Sanpakoi Street Market — небольшой рынок"
    dash_match = re.search(r"^([A-Z0-9\s\'&\.-]{3,35})\s*[—–-]\s*", txt_strip, re.MULTILINE)
    if dash_match:
        cand = clean_title_prefix(dash_match.group(1))
        if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", cand):
            return cand

    # 8. Venue preceded by "в " e.g. "в Chai "N" Thai"
    in_venue_match = re.search(r'\bв\s+(?:кафе|ресторан|коворкинг|баре)?\s*([A-Z][a-zA-Z0-9\s"\'&-]{3,30})\b', txt)
    if in_venue_match:
        cand = clean_title_prefix(in_venue_match.group(1))
        if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES) and not re.search(r"^\d+[\.\–-]", cand):
            return cand

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

def run_strict_cleanup():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reviews")
    all_reviews = cursor.fetchall()

    valid_records = []
    for r in all_reviews:
        txt = r["review_text"] or ""
        txt_lower = txt.lower()

        if any(k in txt_lower for k in VISA_AND_NOISE_KEYWORDS):
            continue

        loc_url = extract_canonical_url(txt)
        venue_name = extract_verified_proper_venue_name(txt, loc_url)

        if not venue_name or venue_name.lower() in GENERIC_TITLES or normalize_name(venue_name) in GENERIC_TITLES:
            continue

        category = determine_category(txt)
        dietary = determine_dietary(txt)
        neighborhood = determine_neighborhood(txt)

        valid_records.append({
            "review": r,
            "title": venue_name,
            "category": category,
            "dietary_type": dietary,
            "neighborhood": neighborhood,
            "location_url": loc_url,
            "text": txt
        })

    # Grouping & Deduplication
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
    print(f"Strict quality cleanup finished! Catalog populated with {inserted_items_count} clean venue items and {inserted_reviews_count} linked reviews.")

if __name__ == "__main__":
    run_strict_cleanup()
