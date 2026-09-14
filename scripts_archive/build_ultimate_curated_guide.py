import sqlite3
import json
import re
import urllib.parse
from datetime import datetime
import os
from database import init_db

PARENT_DIR = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28"
DB_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/chiangmai_guide.db")
CACHE_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/maps_cache.json")
CH_POSTS_PATH = os.path.join(PARENT_DIR, "chiangmai_portal/chiamgmaimy_posts.json")
R3_PATH = os.path.join(PARENT_DIR, "result 3.json")
R4_PATH = os.path.join(PARENT_DIR, "result 4.json")
R5_PATH = os.path.join(PARENT_DIR, "result 5.json")

MONTHS_RU = {
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
    'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
    'сент': 9, 'окт': 10, 'ноя': 11, 'дек': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

REJECT_KEYWORDS = [
    "yellow-tabien-baan", "tabien baan", "табиен баан", "желтая книга", "жёлтая книга",
    "thaicitizenship", "citizenship", "гражданство",
    "dtv", "tourist visa", "student visa", "elite visa", "retirement visa", "виза", "визовый", "визовые",
    "бордер рам", "бордерран", "border run", "visa run", "tm30", "tm6", "tm.30",
    "work permit", "разрешение на работу",
    "resident certificate", "справка о резиденти", "сертификат резидентства",
    "открыть счет", "счет в банке", "карта банкомата", "открытие счета",
    "штамп", "консульство", "посольство", "загранпаспорт",
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "за последние сутки", "в чате обсуждали:", "daily digest",
    "бангкок", "bangkok", "пхукет", "phuket", "паттайя", "pattaya", "самуи", "samui", "убон", "ubon",
    "translate.itparty.club", "itparty.club", "github.com", "wikipedia.org"
]

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
    }
}

FOOD_PAT = re.compile(r'\b(cafe|coffee|restaurant|kitchen|bistro|bar|bakery|pizza|ramen|noodle|tea|grill|vegan|vegetarian|eatery|diner|brewers|roastery|burger|gelato|steakhouse|sushi|kh?ao\s*so[yi]|кафе|ресторан|кофейня|пекарня|пицца|рамен|еда|чайная)\b', re.IGNORECASE)
WORK_PAT = re.compile(r'\b(coworking|co-working|work\s*space|yellow|punspace|hub53|alt_chiangmai|camp\s*maya|heartwork|the\s*story\s*106|star\s*work|wake\s*up|life\s*space)\b', re.IGNORECASE)
SERV_PAT = re.compile(r'\b(hospital|clinic|dental|dentist|dentistry|driving\s*school|rent\s*a\s*car|car\s*rent(?:al)?s?|motor\s*rent(?:al)?s?|bike\s*rent(?:al)?s?|scooter\s*rent(?:al)?s?|laundry|wash\s*&\s*dry|wash\s*and\s*dry|dry\s*clean|immigration|больниц|клиник|стоматолог|автошкол|прачечн)\b', re.IGNORECASE)
WELL_PAT = re.compile(r'\b(massage|spa|sauna|onsen|yoga|hot\s*spring|ice\s*bath|wellness|массаж|спа|сауна|онсен|йога|баня)\b', re.IGNORECASE)
STAY_PAT = re.compile(r'\b(hotel|resort|hostel|residence|guesthouse|condominium|condo|\bvilla\b|apartments?|inn|отель|резорт|хостел|\bвилла\b)\b', re.IGNORECASE)
HIKE_PAT = re.compile(r'\b(trail|trailhead|hike|hiking|nature\s*trail|alltrails|тропа|хайк)\b', re.IGNORECASE)
NATU_PAT = re.compile(r'\b(waterfall|national\s*park|viewpoint|reservoir|botanical\s*garden|cave|canyon|forest\s*park|hot\s*spring|водопад|озеро|смотровая|каньон|пещера|национальный\s*парк|гейзер)\b', re.IGNORECASE)

def clean_place_name(name):
    if not name: return ""
    name = urllib.parse.unquote(name).replace("+", " ")
    name = re.sub(r'^[A-Z0-9]{4}[+\s][A-Z0-9]{2,4}\s*', '', name)
    name = re.sub(r'^\d+\s+', '', name)
    name = re.sub(r'\\u0026(?:amp;)?', '&', name)
    name = re.sub(r'&amp;', '&', name)
    name = re.sub(r'\\[a-zA-Z0-9]+', '', name)
    name = re.sub(r'^[^\w\s"«]+', '', name).strip()
    return re.sub(r'[\s,]+$', '', name).strip()

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

def classify_place(title, address, texts):
    comb = f"{title} {address} " + " ".join(texts[:2])
    if WORK_PAT.search(title): return "workspace"
    if SERV_PAT.search(title): return "services"
    if WELL_PAT.search(title): return "wellness"
    if HIKE_PAT.search(title): return "hiking_trail"
    if NATU_PAT.search(title): return "nature"
    if FOOD_PAT.search(title): return "cafe_restaurant"
    if STAY_PAT.search(title): return "stay"

    if WORK_PAT.search(comb): return "workspace"
    if SERV_PAT.search(comb): return "services"
    if WELL_PAT.search(comb): return "wellness"
    if HIKE_PAT.search(comb): return "hiking_trail"
    if NATU_PAT.search(comb): return "nature"
    if STAY_PAT.search(comb): return "stay"
    if FOOD_PAT.search(comb): return "cafe_restaurant"
    return None

def extract_event_iso_date(event_date_str, title, desc):
    comb = f"{event_date_str or ''} {title or ''} {(desc or '')[:100]}".lower()
    
    # 1. format DD/MM (e.g. 11/09, 28/08, 14/07)
    m1 = re.search(r'(\d{1,2})/(\d{2})', comb)
    if m1:
        d, m = int(m1.group(1)), int(m1.group(2))
        return f"2026-{m:02d}-{d:02d}"

    # 2. format DD-DD Month or DD Month (e.g. 6–7 ноября -> take end date 7 ноября, 11 сентября)
    m2 = re.search(r'(\d{1,2})(?:[–-](\d{1,2}))?\s+([а-яa-z]+)', comb)
    if m2:
        start_d = int(m2.group(1))
        end_d = int(m2.group(2)) if m2.group(2) else start_d
        m_name = m2.group(3)
        if m_name in MONTHS_RU:
            m = MONTHS_RU[m_name]
            return f"2026-{m:02d}-{end_d:02d}"

    # Specific month without day
    m3 = re.search(r'в\s+([а-я]+)', comb)
    if m3 and m3.group(1) in MONTHS_RU:
        m = MONTHS_RU[m3.group(1)]
        return f"2026-{m:02d}-28"

    return None

def extract_event_registration(title, txt, source_link):
    reg_url = ""
    reg_label = ""
    tg_m = re.search(r'(?:запись|регистрация|контакт|писать|бронь|вопросы)[\s\:\—]+@([a-zA-Z0-9_]+)', txt, re.IGNORECASE)
    if tg_m:
        handle = tg_m.group(1)
        reg_url = f"https://t.me/{handle}"
        reg_label = f"Записаться (@{handle})"
    elif "omhome" in (title + txt).lower() or "om home" in (title + txt).lower():
        reg_url = "https://t.me/omhome_cnx"
        reg_label = "Записаться (@omhome_cnx)"
    else:
        ticket_m = re.search(r'(https?://(?:ticket\.[^\s]+|ticketmelon\.com[^\s]+|eventpass\.co[^\s]+|ihaveticket\.com[^\s]+|t\.me/\+[^\s]+|forms\.gle/[^\s]+|docs\.google\.com/forms/[^\s]+|luma\.com/[^\s]+|lin\.ee/[^\s]+))', txt)
        if ticket_m:
            reg_url = ticket_m.group(1)
            reg_label = "Купить билет / Регистрация"
        else:
            phone_m = re.search(r'(?:бронь|столик|заказ|тел)[\s\:\—]+([\d\-\+]{8,15})', txt, re.IGNORECASE)
            if phone_m:
                phone_clean = re.sub(r'[^\d\+]', '', phone_m.group(1))
                reg_url = f"tel:{phone_clean}"
                reg_label = f"Забронировать ({phone_m.group(1).strip()})"
            else:
                if any(w in txt.lower() for w in ["запись обязательна", "запись по ссылке", "регистрация обязательна", "вход по билетам", "купить билеты"]):
                    reg_url = source_link or "https://t.me/ChiamgMaimy"
                    reg_label = "Записаться / Билеты"
    return reg_url, reg_label

def build_catalog():
    init_db()
    maps_cache = load_maps_cache()
    maps_cache["https://maps.app.goo.gl/FcH2vP9WtEEJqSM48"] = [
        "OmHome Space",
        "Pa Daet / Chang Khlan",
        "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
        18.7629,
        98.9955
    ]
    
    url_to_place = {}
    place_info = {}
    for u, entry in maps_cache.items():
        if entry and entry[0] and not entry[0].replace('.', '').isdigit():
            cname = clean_place_name(entry[0])
            if len(cname) >= 3:
                norm_k = cname.lower()
                url_to_place[u] = norm_k
                url_to_place[u.split('?')[0].rstrip('/')] = norm_k
                if norm_k not in place_info:
                    place_info[norm_k] = {
                        'title': cname,
                        'neighborhood': entry[1] if entry[1] else 'Other',
                        'address': entry[2],
                        'lat': entry[3],
                        'lng': entry[4],
                        'url': u
                    }

    # Step 1: Ingest events
    raw_events = []
    if os.path.exists(CH_POSTS_PATH):
        ch_posts = json.load(open(CH_POSTS_PATH, encoding="utf-8"))
        print(f"Ingesting channel posts ({len(ch_posts):,} posts)...")
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
                        iso_d = extract_event_iso_date(d_str, t, ptxt)
                        reg_u, reg_l = extract_event_registration(t, ptxt, link)
                        raw_events.append({
                            "title": t,
                            "venue_name": "OmHome Space",
                            "category": "event",
                            "neighborhood": "Pa Daet / Chang Khlan",
                            "location_url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
                            "address": "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
                            "latitude": 18.7629,
                            "longitude": 98.9955,
                            "event_date": d_str,
                            "event_iso_date": iso_d,
                            "registration_url": reg_u,
                            "registration_label": reg_l,
                            "dietary_type": "none",
                            "description": ptxt,
                            "source_link": link,
                            "sender_name": "@ChiamgMaimy",
                            "msg_id": f"{p_id}_{len(raw_events)}",
                            "msg_date": p_date
                        })
                continue

            # OmHome standalone events
            if "особенный чайный четверг" in txt_lower and ("omhome" in txt_lower or "om home" in txt_lower):
                reg_u, reg_l = extract_event_registration("Особенный чайный четверг", txt, link)
                raw_events.append({
                    "title": "Особенный чайный четверг (Чайная церемония и история Мэ Салонга)",
                    "venue_name": "OmHome Space",
                    "category": "event",
                    "neighborhood": "Pa Daet / Chang Khlan",
                    "location_url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
                    "address": "OmHome Space, Pa Daet, Mueang Chiang Mai District, Chiang Mai 50100",
                    "latitude": 18.7629,
                    "longitude": 98.9955,
                    "event_date": "Четверг 17:00",
                    "event_iso_date": None, # Recurring event
                    "registration_url": reg_u,
                    "registration_label": reg_l,
                    "dietary_type": "none",
                    "description": txt,
                    "source_link": link,
                    "sender_name": "@ChiamgMaimy",
                    "msg_id": f"{p_id}_tea",
                    "msg_date": p_date
                })
                continue

            # Cultural events
            if any(k in txt_lower for k in ["фестиваль", "live concert", "blues night", "workshop", "воркшоп", "fair 2026", "fest 2026"]):
                if not any(r in txt_lower for r in ["сколько стоит жить", "как на концерте", "отзыв", "акции"]):
                    lines = [l.strip() for l in txt.split('\n') if l.strip()]
                    cand_title = clean_place_name(lines[0])
                    cand_title = re.sub(r'^(?:🎶|🌿|🔥|🎸|☕️|🍸|🌲|🎨|🎧|🎷|🎬|🍜|🏃‍♀️|🥑|🍲)\s*', '', cand_title).strip()
                    if cand_title.startswith("http"):
                        if "ticketmelon.com" in cand_title:
                            cand_title = "Sky of Wishes Festival Chiang Mai 2026 (Фестиваль Небесных Фонариков)"
                        else:
                            continue
                    if not is_banter(cand_title) and len(cand_title) >= 5 and len(cand_title) <= 65:
                        venue = ""
                        v_m = re.search(r'(?:📍|в|at|@)\s*([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|School|House|Villa|Hotel|Home|Club|Cocoon|MAIIAM|Attika))\b', txt)
                        if v_m: venue = v_m.group(1).strip()
                        date_m = re.search(r'\b(\d{1,2}(?:[–-]\d{1,2})?\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|сент|окт|ноя|дек|\.\d{2}))', txt, re.IGNORECASE)
                        d_str = date_m.group(1).strip() if date_m else ""
                        iso_d = extract_event_iso_date(d_str, cand_title, txt)
                        reg_u, reg_l = extract_event_registration(cand_title, txt, link)

                        raw_events.append({
                            "title": cand_title,
                            "venue_name": venue or "Chiang Mai",
                            "category": "event",
                            "neighborhood": "Other",
                            "location_url": "",
                            "address": "",
                            "latitude": 0.0,
                            "longitude": 0.0,
                            "event_date": d_str,
                            "event_iso_date": iso_d,
                            "registration_url": reg_u,
                            "registration_label": reg_l,
                            "dietary_type": "none",
                            "description": txt,
                            "source_link": link,
                            "sender_name": "@ChiamgMaimy",
                            "msg_id": p_id,
                            "msg_date": p_date
                        })

    # Step 2: Ingest chat exports
    place_stats = {}
    sources = [(R3_PATH, 'r3'), (R4_PATH, 'r4'), (R5_PATH, 'r5')]
    
    for fpath, sname in sources:
        if not os.path.exists(fpath): continue
        d = json.load(open(fpath, encoding="utf-8"))
        chat_title = d.get("name", sname)
        for m in d.get("messages", []):
            txt = extract_text(m.get("text", "")).strip()
            if len(txt) < 5: continue
            txt_lower = txt.lower()
            if any(k in txt_lower for k in REJECT_KEYWORDS):
                continue

            urls = re.findall(r'https?://[^\s,\)\"\']+', txt)
            matched_places = set()
            for u in urls:
                if 'google.com/maps' in u or 'maps.app.goo.gl' in u or 'goo.gl/maps' in u:
                    u_clean = u.rstrip('.,)')
                    p = url_to_place.get(u_clean) or url_to_place.get(u_clean.split('?')[0].rstrip('/'))
                    if p:
                        matched_places.add((p, u_clean))
            
            for p, u_clean in matched_places:
                if p not in place_stats:
                    place_stats[p] = {'r3': 0, 'r4': 0, 'r5': 0, 'urls': set(), 'reviews': []}
                place_stats[p][sname] += 1
                place_stats[p]['urls'].add(u_clean)
                place_stats[p]['reviews'].append({
                    "msg_id": m.get("id", 0),
                    "sender_name": m.get("from", chat_title),
                    "msg_date": m.get("date", ""),
                    "description": txt.strip(),
                    "source_link": f"https://t.me/{chat_title}/{m.get('id', 0)}" if m.get('id') else ""
                })

    # Step 3: Curate places with targeted quality thresholds
    curated_places = []
    for p, stats in place_stats.items():
        info = place_info.get(p)
        if not info: continue

        r3_cnt = stats['r3']
        r4_cnt = stats['r4']
        r5_cnt = stats['r5']
        total_mentions = r3_cnt + r4_cnt + r5_cnt

        rev_texts = [r['description'] for r in stats['reviews']]
        cat = classify_place(info['title'], info['address'], rev_texts)
        if not cat: continue

        is_included = False
        if cat == 'workspace':
            is_included = (total_mentions >= 1)
        elif cat in ['services', 'stay', 'wellness']:
            is_included = (r3_cnt > 0 or r5_cnt >= 2)
        elif cat == 'hiking_trail':
            is_included = (r4_cnt > 0 or r3_cnt > 0 or r5_cnt >= 2)
        elif cat == 'nature':
            is_included = (r4_cnt > 0 or (r3_cnt > 0 and total_mentions >= 2) or r5_cnt >= 3)
        elif cat == 'cafe_restaurant':
            is_included = ((r3_cnt > 0 and total_mentions >= 2) or r5_cnt >= 3)

        if not is_included:
            continue

        neigh = info['neighborhood']
        addr = info['address']
        lat, lng = info['lat'], info['lng']
        loc_u = list(stats['urls'])[0] if stats['urls'] else info['url']

        for kv, kinfo in KNOWN_VENUE_INFO.items():
            if kv in info['title'].lower():
                neigh = kinfo['neighborhood']
                addr = kinfo['address']
                lat = kinfo['latitude']
                lng = kinfo['longitude']
                loc_u = kinfo['location_url']
                break

        best_desc = ""
        for r in stats['reviews']:
            desc = r['description']
            if len(desc) > len(best_desc):
                best_desc = desc

        curated_places.append({
            "title": info['title'],
            "venue_name": info['title'],
            "category": cat,
            "neighborhood": neigh,
            "location_url": loc_u,
            "address": addr,
            "latitude": lat,
            "longitude": lng,
            "event_date": "",
            "event_iso_date": None,
            "dietary_type": "vegan" if "vegan" in info['title'].lower() else "omnivore",
            "description": best_desc.strip(),
            "mention_count": total_mentions,
            "reviews": stats['reviews']
        })

    # Step 4: Write to SQLite Database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM items")
    c.execute("DELETE FROM reviews")
    c.execute("DELETE FROM sqlite_sequence WHERE name IN ('items', 'reviews')")

    now_str = datetime.now().isoformat()
    ins_items = 0
    ins_reviews = 0

    # Insert events
    for ev in raw_events:
        c.execute("""
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, venue_name, address, latitude, longitude, event_date, event_status, event_iso_date, registration_url, registration_label, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'none', ?, ?, ?, 1, ?, ?)
        """, (
            ev["title"], ev["category"], ev["dietary_type"], ev["neighborhood"],
            ev["description"], ev["location_url"], ev["venue_name"], ev["address"],
            ev["latitude"], ev["longitude"], ev["event_date"], ev["event_iso_date"],
            ev.get("registration_url", ""), ev.get("registration_label", ""),
            now_str, now_str
        ))
        item_id = c.lastrowid
        ins_items += 1

        c.execute("""
            INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, ev["msg_id"], ev["sender_name"], ev["sender_name"],
            ev["msg_date"], ev["description"], "", ev["source_link"]
        ))
        ins_reviews += 1

    # Insert places
    for pl in curated_places:
        c.execute("""
            INSERT INTO items (title, category, dietary_type, neighborhood, description, location_url, venue_name, address, latitude, longitude, event_date, event_status, event_iso_date, registration_url, registration_label, mention_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'none', NULL, '', '', ?, ?, ?)
        """, (
            pl["title"], pl["category"], pl["dietary_type"], pl["neighborhood"],
            pl["description"], pl["location_url"], pl["venue_name"], pl["address"],
            pl["latitude"], pl["longitude"], "", pl["mention_count"],
            now_str, now_str
        ))
        item_id = c.lastrowid
        ins_items += 1

        for r in pl["reviews"]:
            c.execute("""
                INSERT INTO reviews (item_id, telegram_msg_id, channel_username, sender_name, msg_date, review_text, reactions_text, source_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id, r.get("msg_id", 0), r.get("sender_name", ""), r.get("sender_name", ""),
                r.get("msg_date", ""), r.get("description", ""), "", r.get("source_link", "")
            ))
            ins_reviews += 1

    conn.commit()

    c.execute("SELECT category, count(*) FROM items GROUP BY category")
    cats = dict(c.fetchall())
    conn.close()

    print("\n" + "="*60)
    print("🏆 ULTIMATE CURATED GUIDE READY WITH DYNAMIC EVENT DATES!")
    print(f"Total Database Items: {ins_items:,}")
    print(f"Total Reviews: {ins_reviews:,}")
    print("Categories Breakdown:")
    for k, v in cats.items():
        print(f"  • {k}: {v}")
    print("="*60)

if __name__ == "__main__":
    build_catalog()
