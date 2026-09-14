import sqlite3
import json
import re
import urllib.parse
from datetime import datetime
import os

PARENT_DIR = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28"
DB_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/chiangmai_guide.db")
CACHE_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/maps_cache.json")
CH_POSTS_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/chiamgmaimy_posts.json")
TARGET_FILES = ["result 3.json", "result 4.json", "result 5.json"]

REJECT_KEYWORDS = [
    "yellow-tabien-baan", "tabien baan", "табиен баан", "желтая книга", "жёлтая книга",
    "thaicitizenship", "citizenship", "гражданство",
    "dtv", "tourist visa", "student visa", "elite visa", "retirement visa", "виза", "визовый", "визовые",
    "бордер рам", "бордерран", "border run", "visa run", "иммиграци", "immigration", "tm30", "tm6", "tm.30",
    "work permit", "разрешение на работу",
    "resident certificate", "справка о резиденти", "сертификат резидентства",
    "driver license", "driving license", "водительские права", "права на байк", "права в таиланде",
    "открыть счет", "счет в банке", "карта банкомата", "открытие счета",
    "штамп", "консульство", "посольство", "паспорт", "загранпаспорт",
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "аренда кондо", "за последние сутки", "в чате обсуждали:", "daily digest",
    "бангкок", "bangkok", "пхукет", "phuket", "паттайя", "pattaya", "самуи", "samui", "убон", "ubon",
    "translate.itparty.club", "itparty.club", "github.com", "wikipedia.org", "youtube.com", "youtu.be"
]

EXCLUDE_PLACE_TYPES = [
    'condominium', 'condo', 'residence', 'apartment', 'hospital', 'clinic', 'dent', 'dental',
    'rent a car', 'driving school', 'massage', 'spa', 'sauna', 'gym', 'fitness',
    'motor', 'bike', 'repair', 'laundry', 'store', 'shop', 'farm', 'pier',
    'kayak', 'adventure', 'service', 'studio', 'church', 'school', 'optics', 'hotel', 'resort',
    'law', 'office', 'pharmacy', 'gas station', 'petrol', 'parking'
]

FOOD_KEYWORDS = [
    'cafe', 'coffee', 'restaurant', 'kitchen', 'bistro', 'bar', 'bakery', 'pizza',
    'ramen', 'noodle', 'tea', 'grill', 'vegan', 'vegetarian', 'eatery', 'diner',
    'brewers', 'roastery', 'food', 'burgers', 'gelato', 'steakhouse', 'sushi',
    'кафе', 'ресторан', 'кофейня', 'пекарня', 'пицца', 'рамен', 'еда', 'пиво', 'вино', 'чай', 'смузи', 'бургер'
]

NATURE_KEYWORDS = ['waterfall', 'national park', 'lake', 'viewpoint', 'водопад', 'озеро', 'смотровая', 'парк', 'peak']
WORKSPACE_KEYWORDS = ['coworking', 'коворкинг', 'yellow', 'punspace', 'work space']
HIKE_KEYWORDS = ['trail', 'тропа', 'hike', 'хайк', 'alltrails']

BANTER_PATTERNS = [
    r"собираемся\s+",
    r"концерт\s+(?:был|в итоге|идёт|касты)",
    r"на\s+концерт\s+идёт",
    r"но\s+это\s+часто",
    r"зато\s+музыка",
    r"^привее+т",
    r"езжайте\s+на",
    r"в\s+чианграе\s+есть",
    r"у\s+них,?\s+по\s+идее",
    r"фестиваль\s+(?:звучит|начинается|небольшой|там)",
    r"фестиваль\s+свечей\s+в\s+убоне",
    r"друг,\s*кто",
    r"кто\s+(?:в\s+субботу|свободен|покупал|куда)",
    r"поделитесь",
    r"сегодня\s+не\s+успею",
    r"чет\s+переживаю",
    r"не\s+ради\s+концерта",
    r"орган,\s*отвечающий",
    r"хрен\s*с\s*ним",
    r"термальные\s*басики",
    r"главное\s*чтобы",
    r"купил\s*проходки",
    r"билеты\s*в\s*на\s*сайте",
    r"^\d+[\.–-]\d+\s+[а-яА-Яa-zA-Z]+$",
    r"^(всем привет|привет|здравствуйте|добрый день|доброе утро|всем доброе)\b",
    r"\?$",
    r"\.\.\.$",
    r"^(ну|да|не|хотя|кстати|ага|ой|эх|хаха|лол|хз)\s+",
    r"^(были|советую|рекомендую|ищу|где|как|почему|если|мы|вы|планируем)"
]

SUBDISTRICT_MAP = {
    "chang khlan": "Pa Daet / Chang Khlan",
    "pa daet": "Pa Daet / Chang Khlan",
    "padet": "Pa Daet / Chang Khlan",
    "chang moi": "Old City / Chang Moi",
    "phra sing": "Old City",
    "si phum": "Old City",
    "nimman": "Nimman",
    "suthep": "Chang Phueak / Suthep",
    "chang phueak": "Chang Phueak / Suthep",
    "hang dong": "Hang Dong",
    "mae rim": "Mae Rim",
    "mae sa": "Mae Rim",
    "mon jam": "Mae Rim",
    "mae on": "Mae On / Mae Kampong",
    "san kamphaeng": "Mae On / Mae Kampong",
    "san sai": "San Sai",
    "doi suthep": "Doi Suthep",
    "pai": "Pai / Chiang Dao",
    "chiang dao": "Pai / Chiang Dao",
    "chiang rai": "Pai / Chiang Dao"
}

KNOWN_VENUE_INFO = {
    "omhome": {
        "venue_name": "OmHome Space",
        "neighborhood": "Pa Daet / Chang Khlan",
        "location_url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
        "address": "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
        "latitude": 18.7629,
        "longitude": 98.9955
    },
    "soulscape": {
        "venue_name": "Soulscape Community Cafe",
        "neighborhood": "Pai / Chiang Dao",
        "location_url": "https://maps.app.goo.gl/1jQ6VjK8z2eN2VpDA",
        "address": "Soulscape Community Cafe, Pai",
        "latitude": 19.3590,
        "longitude": 98.4410
    },
    "the cocoon": {
        "venue_name": "The Cocoon",
        "neighborhood": "Pai / Chiang Dao",
        "location_url": "https://maps.app.goo.gl/c8z8g48oFfW5hL1v9",
        "address": "The Cocoon, Chiang Rai",
        "latitude": 19.9070,
        "longitude": 99.8320
    },
    "soi dog blues": {
        "venue_name": "Soi Dog Blues Bar",
        "neighborhood": "Old City / Chang Moi",
        "location_url": "https://maps.app.goo.gl/SoiDogBlues",
        "address": "Soi Dog Blues Bar, Chiang Mai",
        "latitude": 18.7900,
        "longitude": 98.9920
    },
    "goodsouls": {
        "venue_name": "Goodsouls Kitchen",
        "neighborhood": "Old City",
        "location_url": "https://maps.app.goo.gl/GoodsoulsKitchen",
        "address": "Goodsouls Kitchen, 52/3 Singharat Rd, Chiang Mai",
        "latitude": 18.7915,
        "longitude": 98.9818
    },
    "yellow coworking": {
        "venue_name": "Yellow Coworking",
        "neighborhood": "Nimman",
        "location_url": "https://maps.app.goo.gl/YellowCoworking",
        "address": "Yellow Coworking, Nimman Soi 9, Chiang Mai",
        "latitude": 18.7972,
        "longitude": 98.9685
    },
    "punspace": {
        "venue_name": "Punspace Coworking",
        "neighborhood": "Nimman",
        "location_url": "https://maps.app.goo.gl/PunspaceNimman",
        "address": "Punspace Coworking, Sirimangkalajarn Soi 11, Chiang Mai",
        "latitude": 18.7955,
        "longitude": 98.9702
    }
}

def clean_place_name(name):
    if not name: return ""
    name = urllib.parse.unquote(name).replace("+", " ")
    name = re.sub(r'^[A-Z0-9]{4}[+\s][A-Z0-9]{2,4}\s*', '', name)
    name = re.sub(r'^\d+\s+', '', name)
    name = re.sub(r'\\u0026(?:amp;)?', '&', name)
    name = re.sub(r'&amp;', '&', name)
    name = re.sub(r'\\[a-zA-Z0-9]+', '', name)
    name = re.sub(r'^[^\w\s"«]+', '', name).strip()
    name = re.sub(r'[\s,]+$', '', name).strip()
    return name

def is_banter(title):
    if not title or len(title) < 3: return True
    t_lower = title.lower()
    for pat in BANTER_PATTERNS:
        if re.search(pat, t_lower): return True
    return False

def extract_text(obj):
    if isinstance(obj, str): return obj
    elif isinstance(obj, list): return "".join([extract_text(item) for item in obj])
    elif isinstance(obj, dict):
        if "text" in obj: return extract_text(obj["text"])
        elif "blocks" in obj: return "\n".join(filter(None, [extract_text(b) for b in obj["blocks"]]))
        elif "content" in obj: return extract_text(obj["content"])
    return ""

def load_maps_cache():
    if os.path.exists(CACHE_PATH):
        try:
            return json.load(open(CACHE_PATH, encoding="utf-8"))
        except Exception: pass
    return {}

def run_build():
    maps_cache = load_maps_cache()
    print(f"Loaded {len(maps_cache):,} Google Maps cache entries.")

    curated_items = []

    # 1. CHANNEL POSTS (@ChiamgMaimy) - FULL 4 MONTHS (1,255 posts)
    if os.path.exists(CH_POSTS_PATH):
        ch_posts = json.load(open(CH_POSTS_PATH, encoding="utf-8"))
        print(f"Curating from full @ChiamgMaimy history ({len(ch_posts):,} posts)...")

        for p in ch_posts:
            txt = p["text"].strip()
            p_id = p["id"]
            p_date = p["date"]
            link = p["link"]
            txt_lower = txt.lower()

            if any(k in txt_lower for k in REJECT_KEYWORDS):
                continue

            # OmHome schedule breakdown
            if ("omhome" in txt_lower or "om home" in txt_lower) and any(k in txt_lower for k in ["расписание", "распиание", "так же на этой неделе", "неделя творчества"]):
                parts = re.split(r'——+|(?=\b\d{1,2}/\d{2}\s*•)', txt)
                for part in parts:
                    ptxt = part.strip()
                    if not ptxt or len(ptxt) < 20: continue
                    date_m = re.search(r'(\d{1,2}/\d{2}\s*•\s*[А-Яа-яA-Za-z]+\s*•\s*\d{1,2}:\d{2})', ptxt)
                    title_m = re.search(r'(?:🍵|🎶|🫖|🎬|🎩|🪐|🧘|🌟)\s*([^\n\r]+)', ptxt)
                    if not title_m:
                        lines = [l.strip() for l in ptxt.split('\n') if l.strip()]
                        for l in lines[1:]:
                            if len(l) > 3 and not l.startswith('💰') and not l.startswith('✍️') and not l.startswith('📍'):
                                title_m = re.match(r'^([^\n\r]+)', l)
                                break
                    if title_m:
                        t = clean_place_name(title_m.group(1))
                        if is_banter(t) or any(k in t.lower() for k in ["расписание", "распиание", "акции"]):
                            continue
                        d_str = date_m.group(1).strip() if date_m else ""
                        curated_items.append({
                            "title": t,
                            "venue_name": "OmHome Space",
                            "category": "event",
                            "neighborhood": "Pa Daet / Chang Khlan",
                            "location_url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
                            "address": "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
                            "latitude": 18.7629,
                            "longitude": 98.9955,
                            "event_date": d_str,
                            "dietary_type": "omnivore",
                            "description": ptxt[:350],
                            "source_link": link,
                            "sender_name": "@ChiamgMaimy",
                            "msg_id": f"{p_id}_{len(curated_items)}",
                            "msg_date": p_date
                        })
                continue

            # OmHome standalone events
            if "особенный чайный четверг" in txt_lower and ("omhome" in txt_lower or "om home" in txt_lower):
                curated_items.append({
                    "title": "Особенный чайный четверг (Чайная церемония и история Мэ Салонга)",
                    "venue_name": "OmHome Space",
                    "category": "event",
                    "neighborhood": "Pa Daet / Chang Khlan",
                    "location_url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
                    "address": "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
                    "latitude": 18.7629,
                    "longitude": 98.9955,
                    "event_date": "Четверг 17:00",
                    "dietary_type": "omnivore",
                    "description": txt[:350],
                    "source_link": link,
                    "sender_name": "@ChiamgMaimy",
                    "msg_id": f"{p_id}_tea",
                    "msg_date": p_date
                })
                continue

            # Cultural events from @ChiamgMaimy
            if any(k in txt_lower for k in ["фестиваль", "live concert", "blues night", "workshop", "воркшоп", "fair 2026", "fest 2026"]):
                if not any(r in txt_lower for r in ["сколько стоит жить", "как на концерте", "отзыв", "акции"]):
                    lines = [l.strip() for l in txt.split('\n') if l.strip()]
                    cand_title = clean_place_name(lines[0])
                    cand_title = re.sub(r'^(?:🎶|🌿|🔥|🎸|☕️|🍸|🌲|🎨|🎧|🎷|🎬|🍜|🏃‍♀️|🥑|🍲)\s*', '', cand_title).strip()
                    if not is_banter(cand_title) and len(cand_title) >= 5 and len(cand_title) <= 55:
                        venue = ""
                        v_m = re.search(r'(?:📍|в|at|@)\s*([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|School|House|Villa|Hotel|Home|Club|Cocoon|MAIIAM))\b', txt)
                        if v_m: venue = v_m.group(1).strip()
                        date_m = re.search(r'\b(\d{1,2}(?:[–-]\d{1,2})?\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|сент|окт|ноя|дек|\.\d{2}))', txt, re.IGNORECASE)
                        d_str = date_m.group(1).strip() if date_m else ""

                        curated_items.append({
                            "title": cand_title,
                            "venue_name": venue or "Chiang Mai",
                            "category": "event",
                            "neighborhood": "Other",
                            "location_url": "",
                            "address": "",
                            "latitude": 0.0,
                            "longitude": 0.0,
                            "event_date": d_str,
                            "dietary_type": "omnivore",
                            "description": txt[:350],
                            "source_link": link,
                            "sender_name": "@ChiamgMaimy",
                            "msg_id": p_id,
                            "msg_date": p_date
                        })

    print(f"Curated {len(curated_items):,} clean events and places from @ChiamgMaimy.")

    # 2. CHAT EXPORTS (result 3, 4, 5.json) - STRICT GOOGLE MAPS / ALLTRAILS LINKS ONLY!
    chat_places_count = 0
    for fname in TARGET_FILES:
        fpath = os.path.join(PARENT_DIR, fname)
        if not os.path.exists(fpath): continue
        data = json.load(open(fpath, encoding="utf-8"))
        chat_name = data.get("name", fname)
        print(f"Scanning verified link places in {fname}...")

        for m in data.get("messages", []):
            txt = extract_text(m.get("text", "")).strip()
            if not txt or len(txt) < 10: continue

            txt_lower = txt.lower()
            if any(k in txt_lower for k in REJECT_KEYWORDS):
                continue

            m_match = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", txt)
            at_match = re.search(r"https?://[\w\.-]*alltrails\.com/trail/[^\s,\)\"\']*", txt)

            title = ""
            venue_name = ""
            neighborhood = "Other"
            address = ""
            lat, lng = 0.0, 0.0
            category = ""
            loc_url = ""

            if at_match:
                loc_url = at_match.group(0).rstrip(".,)")
                at_m = re.search(r"alltrails\.com/trail/[^/\s]+/[^/\s]+/([a-z0-9-]+)", loc_url)
                if at_m:
                    title = at_m.group(1).replace("-", " ").title()
                else:
                    title = "Doi Suthep Trail"
                venue_name = title
                category = "hiking_trail"
                neighborhood = "Doi Suthep"

            elif m_match:
                loc_url = m_match.group(0).rstrip(".,)")
                cache_entry = maps_cache.get(loc_url)
                if not cache_entry:
                    clean_u = loc_url.split("?g_st=")[0]
                    cache_entry = maps_cache.get(clean_u)

                if cache_entry and cache_entry[0]:
                    p_name, p_neigh, p_addr, p_lat, p_lng = cache_entry[:5]
                    clean_p = clean_place_name(p_name)
                    if not clean_p or re.match(r"^\d{1,2}\.\d+$", clean_p) or len(clean_p) < 3:
                        continue
                    if any(k in clean_p.lower() for k in REJECT_KEYWORDS) or any(k in p_addr.lower() for k in REJECT_KEYWORDS):
                        continue
                    if is_banter(clean_p):
                        continue

                    p_lower = (clean_p + " " + txt).lower()

                    # STRICT NON-FOOD EXCLUSION: Skip clinics, dentists, condos, car rentals, mechanics!
                    if any(k in p_lower for k in EXCLUDE_PLACE_TYPES):
                        continue

                    # STRICT CATEGORIZATION
                    if any(k in p_lower for k in WORKSPACE_KEYWORDS):
                        category = "workspace"
                    elif any(k in p_lower for k in NATURE_KEYWORDS):
                        category = "nature"
                    elif any(k in p_lower for k in HIKE_KEYWORDS):
                        category = "hiking_trail"
                    elif any(k in p_lower for k in FOOD_KEYWORDS):
                        category = "cafe_restaurant"
                    else:
                        # DO NOT DEFAULT TO CAFE! Discard non-matching locations!
                        continue

                    title = clean_p
                    venue_name = clean_p
                    neighborhood = p_neigh if p_neigh else "Other"
                    address = p_addr
                    try:
                        lat, lng = float(p_lat), float(p_lng)
                    except Exception:
                        lat, lng = 0.0, 0.0

            if not title or not category or len(title) < 3 or is_banter(title):
                continue

            # Check known venue overrides
            for kv, info in KNOWN_VENUE_INFO.items():
                if kv in title.lower() or kv in txt_lower:
                    venue_name = info["venue_name"]
                    neighborhood = info["neighborhood"]
                    loc_url = info["location_url"]
                    address = info["address"]
                    lat = info["latitude"]
                    lng = info["longitude"]
                    break

            sender_name = m.get("from", chat_name)
            msg_id = m.get("id", 0)
            msg_date = m.get("date", "")
            src_link = f"https://t.me/{chat_name}/{msg_id}" if msg_id else ""

            curated_items.append({
                "title": title,
                "venue_name": venue_name,
                "category": category,
                "neighborhood": neighborhood,
                "location_url": loc_url,
                "address": address,
                "latitude": lat,
                "longitude": lng,
                "event_date": "",
                "dietary_type": "omnivore",
                "description": txt[:300],
                "source_link": src_link,
                "sender_name": sender_name,
                "msg_id": msg_id,
                "msg_date": msg_date
            })
            chat_places_count += 1

    print(f"Curated {chat_places_count:,} strictly categorized places from chat.")
    print(f"Total curated entities before deduplication: {len(curated_items):,}")

    # 3. DEDUPLICATION & DATABASE INSERTION
    grouped = {}
    for it in curated_items:
        loc = it["location_url"]
        t = it["title"]
        cat = it["category"]
        norm = re.sub(r"[^\w\s]", "", t.lower()).strip()

        if cat == "event":
            key = f"EVENT:{norm}:{it.get('event_date', '')}"
        elif loc:
            key = f"URL:{loc}"
        elif norm and len(norm) > 2:
            key = f"TITLE:{cat}:{norm}"
        else:
            key = f"ID:{it['msg_id']}"

        if key not in grouped:
            grouped[key] = {
                "title": t,
                "venue_name": it["venue_name"],
                "category": cat,
                "dietary_type": it["dietary_type"],
                "neighborhood": it["neighborhood"],
                "description": it["description"],
                "location_url": loc,
                "address": it["address"],
                "latitude": it["latitude"],
                "longitude": it["longitude"],
                "event_date": it["event_date"],
                "reviews": [it]
            }
        else:
            g = grouped[key]
            g["reviews"].append(it)
            if len(t) > len(g["title"]): g["title"] = t
            if not g["venue_name"] and it["venue_name"]: g["venue_name"] = it["venue_name"]
            if g["neighborhood"] == "Other" and it["neighborhood"] != "Other": g["neighborhood"] = it["neighborhood"]
            if not g["address"] and it["address"]: g["address"] = it["address"]
            if not g["latitude"] and it["latitude"]:
                g["latitude"] = it["latitude"]
                g["longitude"] = it["longitude"]

    print(f"Deduplicated into {len(grouped):,} pristine catalog entities.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM items")
    c.execute("DELETE FROM reviews")
    c.execute("DELETE FROM sqlite_sequence WHERE name IN ('items', 'reviews')")

    now_str = datetime.now().isoformat()
    ins_items = 0
    ins_reviews = 0

    for key, g in grouped.items():
        mention_count = len(g["reviews"])
        c.execute("""
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, venue_name, address, latitude, longitude, event_date, event_status, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'none', ?, ?, ?)
        """, (
            g["title"], g["category"], g["dietary_type"], g["neighborhood"],
            g["description"], g["location_url"], g["venue_name"], g["address"],
            g["latitude"], g["longitude"], g["event_date"], mention_count,
            now_str, now_str
        ))
        item_id = c.lastrowid
        ins_items += 1

        for r in g["reviews"]:
            c.execute("""
                INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id, r["msg_id"], r.get("sender_name", ""), r.get("sender_name", ""),
                r.get("msg_date", ""), r["description"], "", r["source_link"]
            ))
            ins_reviews += 1

    conn.commit()

    c.execute("SELECT category, count(*) FROM items GROUP BY category")
    cats = dict(c.fetchall())
    c.execute("SELECT neighborhood, count(*) FROM items GROUP BY neighborhood")
    neighs = dict(c.fetchall())
    conn.close()

    print("\n" + "="*60)
    print("🏆 FINAL BALANCED GUIDE BUILT SUCCESSFULLY!")
    print(f"📊 Pure Entities in Database: {ins_items:,}")
    print(f"💬 Linked Reviews/Posts: {ins_reviews:,}")
    print("Categories:", cats)
    print("Neighborhoods:", neighs)
    print("="*60)

if __name__ == "__main__":
    run_build()
