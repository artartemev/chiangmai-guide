import sqlite3
import re
import urllib.parse
from datetime import datetime

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"

# Blacklist of visa, legal, rental, non-venue websites, and non-Chiang Mai cities
REJECT_KEYWORDS = [
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
    # Rentals & Housing
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "аренда кондо", "за последние сутки", "в чате обсуждали:", "daily digest",
    # Non-Chiang Mai Cities
    "бангкок", "bangkok", "пхукет", "phuket", "паттайя", "pattaya", "самуи", "samui",
    # Non-venue websites & IT tools
    "translate.itparty.club", "itparty.club", "github.com", "wikipedia.org"
]

# Banter, personal opinion, past recollections, questions, and conversational noise
BANTER_PATTERNS = [
    r"орган,\s*отвечающий",
    r"не ради концерта",
    r"кто\s*нибудь\s*покупал",
    r"планирую\s*перебираться",
    r"как\s*на\s*концерте",
    r"последний\s*концерт",
    r"хрен\s*с\s*ним",
    r"термальные\s*басики",
    r"главное\s*чтобы",
    r"купил\s*проходки",
    r"билеты\s*в\s*на\s*сайте",
    r"^\d+[\.–-]\d+\s+[а-яА-Яa-zA-Z]+", # Date only titles
    r"^(всем привет|привет|здравствуйте|добрый день|доброе утро|всем доброе)\b",
    r"\?$", # Any sentence ending with a question mark

    r"^(ну|да|не|хтя|кстати|ага|ой|эх|хаха|лол|хз)\s+",
    r"^(были|советую|рекомендую|ищу|кто|где|как|почему|если|мы|вы|собираемся|планируем|поделитесь)",
    r"^(встречаемся|стартуем|точка сбора|тропа протяженностью|alltrails)"
]

NEIGHBORHOOD_KEYWORDS = {
    "Pa Daet / Chang Khlan": ["pa daet", "padet", "chang khlan", "па дэт", "падаэт", "чанг кхлан", "omhome", "om home", "омхоум", "ом хоум"],
    "Nimman": ["nimman", "нимман", "нимманхем", "sirimangkalajarn", "сириманкаладжарн", "one nimman", "huay kaew", "хуай кэв", "warm up", "maya", "маия"],
    "Old City": ["old city", "старый город", "старом город", "рахдамноен", "rachadamnoen", "phra sing", "пхра синг", "thapae", "тхапхэ", "moon muang", "мунай муанг", "wat chedi luang", "чеди луанг"],
    "Santitham": ["santitham", "сантитам", "сантитхам"],
    "Chang Phueak / Suthep": ["chang phueak", "чанг пыак", "jed yod", "джед йод", "cmu", "университет чиангмая", "кад суан каео", "suthep", "сутеп", "сутхеп"],
    "Hang Dong": ["hang dong", "ханг донг", "хангдонг", "kad farang", "кад фаранг", "grand canyon", "гранд каньон", "mae hia", "мае хиа", "night safari"],
    "Mae Rim": ["mae rim", "мае рим", "маерим", "mae sa", "мае са", "mon jam", "мон джам", "pang hwa", "панг хва"],
    "Mae On": ["mae kampong", "мае кампонг", "май кампонг", "mae on", "мае он", "hot springs", "горячие источники", "san kamphaeng", "сан камфаенг"],
    "Doi Suthep": ["doi suthep", "дой сутеп", "дой сутхеп", "wat pha lat", "ват пха лат", "monk's trail", "monks trail", "тропа монахов", "doi pui", "дой пуи", "kew mae pan"],
    "San Sai": ["san sai", "сан сай", "сансай", "mae jo", "мае джо", "ruamchok", "руамчок", "central festival", "централ фестиваль"],
    "Pai / Chiang Dao": ["pai", "пае", "паи", "пай", "chiang dao", "чиангдао", "чианг дао", "chiang rai", "чианграй", "singha park", "сингха парк", "mae hong son", "белый храм", "синий храм", "soulscape", "the cocoon"]
}

KNOWN_VENUE_NEIGHBORHOODS = {
    "soulscape community cafe": "Pai / Chiang Dao",
    "soulscape": "Pai / Chiang Dao",
    "the cocoon": "Pai / Chiang Dao",
    "omhome": "Pa Daet / Chang Khlan",
    "om home": "Pa Daet / Chang Khlan",
    "goodsouls kitchen": "Old City",
    "yellow coworking": "Nimman",
    "punspace": "Nimman",
    "camp maya": "Nimman",
    "singha park": "Pai / Chiang Dao",
    "attika studio": "Nimman",
    "basecamp trail cafe": "Doi Suthep",
    "vaanaa cafe & bistro": "Chang Phueak / Suthep",
    "the nest school chiang mai": "Old City"
}

KNOWN_VENUE_MAPS = {
    "omhome": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
    "om home": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48"
}


def normalize_name(name):
    return re.sub(r"[^\w\s]", "", name.lower()).strip()

def clean_title_text(text):
    if not text:
        return ""
    text = re.sub(r"^(?:сохраняйте себе!|сохраняйте себе|сохраняйте|карта фестиваля|карта|смотрите какую|ловите|делимся|всем советую|напоминаем!|напоминаем)\s*[:!—–-]*\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^(?:📍|Где:\s*|Где\s*:\s*|Локация:\s*)", "", text, flags=re.IGNORECASE).strip()
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

import json
import os

CACHE_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/maps_cache.json"
MAPS_CACHE = {}

def load_maps_cache():
    global MAPS_CACHE
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                MAPS_CACHE = json.load(f)
            print(f"Loaded {len(MAPS_CACHE):,} Google Maps cache entries into curator.")
        except Exception:
            MAPS_CACHE = {}

load_maps_cache()

def determine_neighborhood(txt, venue_name="", loc_url=""):
    if loc_url in MAPS_CACHE:
        val = MAPS_CACHE[loc_url]
        if len(val) >= 2 and val[1] and val[1] != "Other":
            return val[1]

    lower = (txt + " " + venue_name).lower()
    for kv, neigh in KNOWN_VENUE_NEIGHBORHOODS.items():
        if kv in lower:
            return neigh
    for neigh, kws in NEIGHBORHOOD_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            return neigh
    return "Other"

def process_thoughtful_entity(txt, loc_url=""):
    if not txt or len(txt) < 10:
        return None

    txt_clean = clean_title_text(txt)
    txt_lower = txt.lower()

    # 1. Hard rejection of blacklist keywords
    if any(k in txt_lower for k in REJECT_KEYWORDS):
        return None

    # 2. Hard rejection of banter, questions, complaints, past recollections
    for pat in BANTER_PATTERNS:
        if re.search(pat, txt_lower):
            return None

    # 3. Categorization & Title extraction
    is_event = False
    if any(k in txt_lower for k in ["митап", "ивент", "фестиваль", "концерт", "вечеринка", "event", "meetup", "party", "воркшоп", "workshop", "поэтический вечер", "чайная церемония", "чайный четверг", "выставка", "ярмарка", "festival"]):
        if not any(r in txt_lower for r in ["обзор", "кофейных мест", "four cafés", "several cafes", "top cafes", "как на концерте"]):
            is_event = True

    title = ""
    venue_name = ""
    event_date = ""

    date_match = re.search(r"\b(\d{1,2}\s*(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\.\d{2}))", txt_lower)
    if date_match:
        event_date = date_match.group(0)

    if is_event:
        # OmHome Event
        if "omhome" in txt_lower or "om home" in txt_lower or "омхоум" in txt_lower or "ом хоум" in txt_lower:
            venue_name = "OmHome"
            if "чайный" in txt_lower or "чайная" in txt_lower:
                title = "Особенный чайный четверг (Чайная церемония)"
            elif "поэтическ" in txt_lower or "стихи" in txt_lower:
                title = "Поэтический вечер в Om Home"
            else:
                title = "Мероприятие в Om Home"

        # Chiang Mai Music Journey 9
        elif "music journey" in txt_lower:
            title = "Chiang Mai Music Journey 9"
            venue_name = "Chiang Mai"

        # Soulscape Event
        elif "soulscape" in txt_lower and "dj workshop" in txt_lower:
            title = "DJ WORKSHOP & Listening Session"
            venue_name = "Soulscape Community Cafe"

        # The Cocoon Event
        elif "the cocoon" in txt_lower and "2nd last event" in txt_lower:
            title = "2nd Last Event at The Cocoon"
            venue_name = "The Cocoon"

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
                cand = clean_title_text(lines[0])
                cand = re.sub(r"[^\w\s\.-]+$", "", cand).strip()
                if len(cand) >= 3 and len(cand) <= 55 and not cand.endswith("?"):
                    title = cand

        if not venue_name:
            v_match = re.search(r'(?:📍|в|at|@)\s*([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|School|House|Villa|Hotel|Home|Club|Cocoon))\b', txt, re.IGNORECASE)
            if v_match:
                venue_name = clean_title_text(v_match.group(1))

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
                cand = clean_title_text(pin_match.group(1))
                if len(cand) >= 3 and not cand.endswith("?"):
                    title = cand

            if not title:
                eng_quoted = re.search(r'\b([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|Bakery|Bar|Trail|Waterfall|Coworking|Hub|House|Villa|Hotel|Retreat|Farm|Baan|Thai|Tea|Tapas|Grill|Noodle|Pizza|Sushi|Vegan|Club))\b', txt)
                if eng_quoted:
                    cand = clean_title_text(eng_quoted.group(1))
                    if len(cand) >= 3 and not cand.endswith("?"):
                        title = cand

            if not title:
                ru_quote = re.search(r'(?:кафе|ресторан|водопад|коворкинг|тропа|хайк|отель|бар|храм|рынок|парк)\s+["«]([^"»]+)["»]', txt, re.IGNORECASE)
                if ru_quote:
                    cand = clean_title_text(ru_quote.group(1))
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

    title = clean_title_text(title)
    if not title or len(title) < 3 or title.lower() in [g.lower() for g in BANTER_PATTERNS]:
        return None

    for kv, map_url in KNOWN_VENUE_MAPS.items():
        if kv in txt_lower or kv in venue_name.lower():
            if not loc_url:
                loc_url = map_url

    dietary = "none"

    if "веган" in txt_lower or "vegan" in txt_lower:
        dietary = "vegan"
    elif "вегетариан" in txt_lower or "vegetarian" in txt_lower:
        dietary = "vegetarian"
    elif any(k in txt_lower for k in ["кофе", "coffee", "кофейн", "matcha"]):
        dietary = "coffee_only"
    else:
        dietary = "omnivore"

    address = ""
    latitude = 0.0
    longitude = 0.0

    if loc_url in MAPS_CACHE:
        val = MAPS_CACHE[loc_url]
        if len(val) >= 5:
            p_name, p_neigh, p_addr, p_lat, p_lng = val[:5]
            if p_name and not venue_name:
                venue_name = p_name
            if p_name and not is_event and (not title or len(title) > 40):
                title = p_name
            if p_addr:
                address = p_addr
            if p_lat and p_lng:
                try:
                    latitude = float(p_lat)
                    longitude = float(p_lng)
                except Exception:
                    pass

    neighborhood = determine_neighborhood(txt, venue_name, loc_url)

    return {
        "title": title,
        "venue_name": venue_name,
        "category": category,
        "dietary_type": dietary,
        "neighborhood": neighborhood,
        "location_url": loc_url,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "event_date": event_date,
        "description": txt[:300].strip()
    }

def run_thoughtful_builder():
    load_maps_cache()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for col, col_type in [("venue_name", "TEXT DEFAULT ''"), ("address", "TEXT DEFAULT ''"), ("latitude", "REAL DEFAULT 0.0"), ("longitude", "REAL DEFAULT 0.0"), ("opening_hours", "TEXT DEFAULT ''"), ("phone_contact", "TEXT DEFAULT ''"), ("website", "TEXT DEFAULT ''")]:
        try:
            cursor.execute(f"ALTER TABLE items ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    cursor.execute("SELECT * FROM reviews")
    all_reviews = cursor.fetchall()
    print(f"Loaded {len(all_reviews):,} total reviews from database for thoughtful curation.")

    valid_records = []
    events_count = 0
    venues_count = 0

    for r in all_reviews:
        txt = r["review_text"] or ""
        loc_url = extract_canonical_url(txt)
        
        parsed = process_thoughtful_entity(txt, loc_url)
        if not parsed:
            continue

        parsed["review"] = r
        valid_records.append(parsed)

        if parsed["category"] == "event":
            events_count += 1
        else:
            venues_count += 1

    print(f"Thoughtfully curated {len(valid_records):,} valid entities (Events: {events_count:,}, Venues/Places: {venues_count:,})")

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
                "address": rec.get("address", ""),
                "latitude": rec.get("latitude", 0.0),
                "longitude": rec.get("longitude", 0.0),
                "event_date": rec["event_date"],
                "reviews": [rec["review"]]
            }
        else:
            g = grouped_items[group_key]
            g["reviews"].append(rec["review"])
            if len(title) > len(g["title"]):
                g["title"] = title
            if not g["venue_name"] and rec["venue_name"]:
                g["venue_name"] = rec["venue_name"]
            if g["location_url"] == "" and loc_url:
                g["location_url"] = loc_url
            if g["neighborhood"] == "Other" and rec["neighborhood"] != "Other":
                g["neighborhood"] = rec["neighborhood"]
            if not g.get("address") and rec.get("address"):
                g["address"] = rec["address"]
            if not g.get("latitude") and rec.get("latitude"):
                g["latitude"] = rec["latitude"]
                g["longitude"] = rec["longitude"]

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
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, venue_name, address, latitude, longitude, event_date, event_status, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'none', ?, ?, ?)
        """, (
            item["title"],
            item["category"],
            item["dietary_type"],
            item["neighborhood"],
            item["description"],
            item["location_url"],
            item["venue_name"],
            item.get("address", ""),
            item.get("latitude", 0.0),
            item.get("longitude", 0.0),
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

    print("\n🎉 THOUGHTFUL BUILD COMPLETE!")
    print(f"📊 Total Entities in Database: {inserted_items_count:,}")
    print(f"💬 Total Linked User Reviews: {inserted_reviews_count:,}")
    print("\nCategories Stats:", dict(cat_stats))
    print("Neighborhoods Stats:", dict(neigh_stats))

if __name__ == "__main__":
    run_thoughtful_builder()
