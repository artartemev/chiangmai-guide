import sqlite3
import re
import urllib.parse
from datetime import datetime

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"

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
    "то есть фенси веган боул?", "так, предлагаю новую тему:", "точка сбора", "alltrails"
]

NEIGHBORHOOD_KEYWORDS = {
    "Nimman": ["nimman", "нимман", "нимманхем", "sirimangkalajarn", "сириманкаладжарн", "one nimman", "huay kaew", "хуай кэв", "warm up", "maya", "маия"],
    "Old City": ["old city", "старый город", "старом город", "рахдамноен", "rachadamnoen", "phra sing", "пхра синг", "thapae", "тхапхэ", "moon muang", "мунай муанг", "wat chedi luang", "чеди луанг"],
    "Santitham": ["santitham", "сантитам", "сантитхам"],
    "Chang Phueak": ["chang phueak", "чанг пыак", "чанг пыак", "jed yod", "джед йод", "cmu", "университет чиангмая", "кад суан каео"],
    "Hang Dong": ["hang dong", "ханг донг", "хангдонг", "kad farang", "кад фаранг", "grand canyon", "гранд каньон", "mae hia", "мае хиа", "night safari", "omhome", "om home"],
    "Mae Rim": ["mae rim", "мае рим", "маерим", "mae sa", "мае са", "mon jam", "мон джам", "мон джам", "pang hwa", "панг хва"],
    "Mae On": ["mae kampong", "мае кампонг", "май кампонг", "mae on", "мае он", "hot springs", "горячие источники", "san kamphaeng", "сан камфаенг"],
    "Doi Suthep": ["doi suthep", "дой сутеп", "дой сутхеп", "wat pha lat", "ват пха лат", "monk's trail", "monks trail", "тропа монахов", "doi pui", "дой пуи", "kew mae pan"],
    "San Sai": ["san sai", "сан сай", "сансай", "mae jo", "мае джо", "ruamchok", "руамчок", "central festival", "централ фестиваль"],
    "Pai / Chiang Dao": ["pai", "пае", "паи", "пай", "chiang dao", "чиангдао", "чианг дао", "chiang rai", "чианграй", "singha park", "сингха парк", "mae hong son", "белый храм", "синий храм", "soulscape"]
}

KNOWN_VENUE_NEIGHBORHOODS = {
    "soulscape community cafe": "Pai / Chiang Dao",
    "soulscape": "Pai / Chiang Dao",
    "omhome": "Hang Dong",
    "om home": "Hang Dong",
    "goodsouls kitchen": "Old City",
    "yellow coworking": "Nimman",
    "punspace": "Nimman",
    "camp maya": "Nimman",
    "singha park": "Pai / Chiang Dao",
    "attika studio": "Nimman",
    "basecamp trail cafe": "Doi Suthep",
    "vaanaa cafe & bistro": "Chang Phueak",
    "the nest school chiang mai": "Old City"
}

def normalize_name(name):
    return re.sub(r"[^\w\s]", "", name.lower()).strip()

def clean_social_media_cta(text):
    if not text:
        return ""
    text = re.sub(r"^(?:сохраняйте себе!|сохраняйте себе|сохраняйте|карта фестиваля|карта|смотрите какую|ловите|делимся|всем советую|напоминаем!|напоминаем)\s*[:!—–-]*\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^(?:📍|Где:\s*|Где\s*:\s*|Локация:\s*)", "", text, flags=re.IGNORECASE).strip()
    # Fix trailing Russian prepositions
    text = re.sub(r"\s+(?:в|на|с|от|для|и)$", "", text, flags=re.IGNORECASE).strip()
    return text

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

def determine_neighborhood(txt, venue_name=""):
    lower = (txt + " " + venue_name).lower()
    
    for kv, neigh in KNOWN_VENUE_NEIGHBORHOODS.items():
        if kv in lower:
            return neigh

    for neigh, kws in NEIGHBORHOOD_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            return neigh

    return "Other"

def process_entity(txt, loc_url=""):
    if not txt:
        return None

    txt_clean = clean_social_media_cta(txt)
    txt_lower = txt.lower()

    if any(k in txt_lower for k in VISA_AND_NOISE_KEYWORDS):
        return None

    # Check category: Event vs Venue vs Cafe Roundup
    is_event = False
    if any(k in txt_lower for k in ["митап", "ивент", "фестиваль", "концерт", "вечеринка", "event", "meetup", "party", "воркшоп", "workshop", "поэтический вечер", "чайная церемония", "чайный четверг", "выставка", "ярмарка", "festival"]):
        if not any(r in txt_lower for r in ["обзор", "кофейных мест", "four cafés", "several cafes", "top cafes"]):
            is_event = True

    title = ""
    venue_name = ""
    event_date = ""

    date_match = re.search(r"\b(\d{1,2}\s*(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\.\d{2}))", txt_lower)
    if date_match:
        event_date = date_match.group(0)

    if is_event:
        # OmHome Event specific handling
        if "omhome" in txt_lower or "om home" in txt_lower:
            venue_name = "OmHome"
            if "чайный" in txt_lower or "чайная" in txt_lower:
                title = "Особенный чайный четверг (Чайная церемония)"
            elif "поэтическ" in txt_lower or "стихи" in txt_lower:
                title = "Поэтический вечер в Om Home"
            else:
                title = "Мероприятие в Om Home"

        # Chiang Mai Music Journey 9
        elif "music journey 9" in txt_lower or "music journey" in txt_lower:
            title = "Chiang Mai Music Journey 9"
            venue_name = "Chiang Mai"

        # Soulscape Event
        elif "soulscape" in txt_lower and "dj workshop" in txt_lower:
            title = "DJ WORKSHOP & Listening Session"
            venue_name = "Soulscape Community Cafe"

        # General Event Patterns
        if not title:
            ws_match = re.search(r'\b([A-Z0-9\s"\'&-]{3,40}(?:WORKSHOP|Workshop|Fest|Festival|Party|Session|Live|Concert|Fair|Market|Journey))\b', txt_clean)
            if ws_match:
                title = ws_match.group(1).strip()
            
        if not title:
            ru_evt = re.search(r'\b((?:Поэтический вечер|Чайная церемония|Мастер-класс|Музыкальный фест|Фестиваль|Воркшоп|Концерт|Вечеринка|Митап)\s+[A-ZА-Яа-я0-9\s"«»-]{2,30})\b', txt_clean)
            if ru_evt:
                title = ru_evt.group(1).strip()

        if not title:
            q_evt = re.search(r'["«]([^"»]{3,40})["»]', txt_clean)
            if q_evt and any(k in q_evt.group(1).lower() for k in ["fest", "music", "workshop", "party", "fair", "journey"]):
                title = q_evt.group(1).strip()

        if not title:
            lines = [l.strip() for l in txt_clean.split("\n") if l.strip()]
            if lines:
                cand = clean_social_media_cta(lines[0])
                cand = re.sub(r"[^\w\s\.-]+$", "", cand).strip()
                if len(cand) >= 3 and len(cand) <= 55 and not cand.endswith("?"):
                    title = cand

        if not venue_name:
            v_match = re.search(r'(?:📍|в|at|@)\s*([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|School|House|Villa|Hotel|Home|Club))\b', txt, re.IGNORECASE)
            if v_match:
                venue_name = clean_social_media_cta(v_match.group(1))

        if not title:
            return None

        category = "event"

    else:
        # VENUE / PLACE EXTRACTION
        if "обзор 4-х кофейных мест" in txt_lower or "four cafés" in txt_lower or "their food also brings together" in txt_lower:
            title = "Обзор кофейных мест Чиангмая"
            venue_name = "Chiang Mai Cafes"
        else:
            pin_match = re.search(r"(?:📍|Где:\s*)\s*([^\n\r,\.\?]+)", txt, re.IGNORECASE)
            if pin_match:
                cand = clean_social_media_cta(pin_match.group(1))
                if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES):
                    title = cand

            if not title:
                eng_quoted = re.search(r'\b([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|Bakery|Bar|Trail|Waterfall|Coworking|Hub|House|Villa|Hotel|Retreat|Farm|Baan|Thai|Tea|Tapas|Grill|Noodle|Pizza|Sushi|Vegan|Club))\b', txt)
                if eng_quoted:
                    cand = clean_social_media_cta(eng_quoted.group(1))
                    if len(cand) >= 3 and not cand.endswith("?") and not any(cand.lower().startswith(p) for p in CHAT_QUESTION_PREFIXES):
                        title = cand

            if not title:
                ru_quote = re.search(r'(?:кафе|ресторан|водопад|коворкинг|тропа|хайк|отель|бар|храм|рынок|парк)\s+["«]([^"»]+)["»]', txt, re.IGNORECASE)
                if ru_quote:
                    cand = clean_social_media_cta(ru_quote.group(1))
                    if len(cand) >= 3 and not cand.endswith("?"):
                        title = cand

            if not title and "alltrails.com" in loc_url:
                at_match = re.search(r"alltrails\.com/trail/[^/\s]+/[^/\s]+/([a-z0-9-]+)", loc_url)
                if at_match:
                    title = at_match.group(1).replace("-", " ").title()

            if not title and loc_url:
                q_match = re.search(r"[?&]q=([^&\s]+)", loc_url)
                if q_match:
                    val = urllib.parse.unquote(q_match.group(1)).replace("+", " ").strip()
                    if val and not val.replace(".", "").isdigit() and len(val) > 2 and not val.endswith("?"):
                        title = val

            if not title:
                return None

            venue_name = title

        if any(k in txt_lower for k in ["коворкинг", "coworking", "рабоч space", "hub", "yellow coworking", "punspace"]):
            category = "workspace"
        elif any(k in txt_lower for k in ["водопад", "waterfall", "каньон", "слоны", "слон", "озеро", "гора", "nature", "дои интанон", "viewpoint"]):
            category = "nature"
        elif any(k in txt_lower for k in ["хайк", "хайкинг", "трек", "тропа", "trail", "hike", "hiking", "monk trail"]):
            category = "hiking_trail"
        else:
            category = "cafe_restaurant"

    # Clean venue_name if it is a raw URL
    if venue_name.startswith("http"):
        venue_name = ""

    # Clean title final check
    title = clean_social_media_cta(title)
    if not title or len(title) < 3 or title.lower() in GENERIC_TITLES or normalize_name(title) in GENERIC_TITLES:
        return None

    # Reject date-only titles e.g. "4–6 ноября 2025" or greetings like "Всем доброе утро."
    if re.search(r"^\d+[\.–-]\d+\s+[а-яА-Яa-zA-Z]+", title) or title.lower().startswith("всем доброе"):
        return None

    dietary = "none"
    if "веган" in txt_lower or "vegan" in txt_lower:
        dietary = "vegan"
    elif "вегетариан" in txt_lower or "vegetarian" in txt_lower:
        dietary = "vegetarian"
    elif any(k in txt_lower for k in ["кофе", "coffee", "кофейн", "matcha"]):
        dietary = "coffee_only"
    else:
        dietary = "omnivore"

    neighborhood = determine_neighborhood(txt, venue_name)

    return {
        "title": title,
        "venue_name": venue_name,
        "category": category,
        "dietary_type": dietary,
        "neighborhood": neighborhood,
        "location_url": loc_url,
        "event_date": event_date,
        "description": txt[:300].strip()
    }

def run_pro_builder():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE items ADD COLUMN venue_name TEXT DEFAULT ''")
    except Exception:
        pass

    cursor.execute("SELECT * FROM reviews")
    all_reviews = cursor.fetchall()
    print(f"Loaded {len(all_reviews):,} total reviews from database for semantic curation.")

    valid_records = []
    events_count = 0
    venues_count = 0

    for r in all_reviews:
        txt = r["review_text"] or ""
        loc_url = extract_canonical_url(txt)
        
        parsed = process_entity(txt, loc_url)
        if not parsed:
            continue

        parsed["review"] = r
        valid_records.append(parsed)

        if parsed["category"] == "event":
            events_count += 1
        else:
            venues_count += 1

    print(f"Parsed {len(valid_records):,} valid entities (Events: {events_count:,}, Venues/Places: {venues_count:,})")

    grouped_items = {}

    for rec in valid_records:
        loc_url = rec["location_url"]
        title = rec["title"]
        norm_t = normalize_name(title)
        cat = rec["category"]

        if loc_url:
            group_key = f"URL:{loc_url}"
        elif norm_t and len(norm_t) > 2:
            group_key = f"TITLE:{cat}:{norm_t}"
        else:
            group_key = f"REV:{rec['review']['id']}"

        if group_key not in grouped_items:
            grouped_items[group_key] = {
                "title": title,
                "venue_name": rec["venue_name"],
                "category": cat,
                "dietary_type": rec["dietary_type"],
                "neighborhood": rec["neighborhood"],
                "description": rec["description"],
                "location_url": loc_url,
                "event_date": rec["event_date"],
                "reviews": [rec["review"]]
            }
        else:
            g = grouped_items[group_key]
            g["reviews"].append(rec["review"])
            if len(title) > len(g["title"]) and title.lower() not in GENERIC_TITLES:
                g["title"] = title
            if not g["venue_name"] and rec["venue_name"]:
                g["venue_name"] = rec["venue_name"]
            if g["location_url"] == "" and loc_url:
                g["location_url"] = loc_url
            if g["neighborhood"] == "Other" and rec["neighborhood"] != "Other":
                g["neighborhood"] = rec["neighborhood"]

    print(f"Deduplicated into {len(grouped_items):,} high-precision catalog entities.")

    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('items', 'reviews')")

    now_str = datetime.now().isoformat()
    inserted_items_count = 0
    inserted_reviews_count = 0

    for key, item in grouped_items.items():
        mention_count = len(item["reviews"])
        cursor.execute("""
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, venue_name, event_date, event_status, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'none', ?, ?, ?)
        """, (
            item["title"],
            item["category"],
            item["dietary_type"],
            item["neighborhood"],
            item["description"],
            item["location_url"],
            item["venue_name"],
            item["event_date"],
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

    cursor.execute("SELECT neighborhood, count(*) FROM items GROUP BY neighborhood")
    neigh_stats = cursor.fetchall()
    cursor.execute("SELECT category, count(*) FROM items GROUP BY category")
    cat_stats = cursor.fetchall()

    conn.close()

    print("\n🎉 BUILD PRO CATALOG COMPLETE!")
    print(f"📊 Total Entities in Database: {inserted_items_count:,}")
    print(f"💬 Total Linked User Reviews: {inserted_reviews_count:,}")
    print("\nCategories Stats:", dict(cat_stats))
    print("Neighborhoods Stats:", dict(neigh_stats))

if __name__ == "__main__":
    run_pro_builder()
