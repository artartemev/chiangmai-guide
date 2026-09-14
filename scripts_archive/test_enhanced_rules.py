import sqlite3
import re
import urllib.parse

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"

BLACK_KEYWORDS = [
    "yellow-tabien-baan", "tabien baan", "табиен баан", "желтая книга", "жёлтая книга",
    "thaicitizenship", "citizenship", "гражданство",
    "dtv", "tourist visa", "student visa", "elite visa", "retirement visa", "виза", "визовый", "визовые",
    "бордер рам", "бордерран", "border run", "visa run", "иммиграци", "immigration", "tm30", "tm6", "tm.30",
    "work permit", "разрешение на работу",
    "resident certificate", "справка о резиденти", "сертификат резидентства",
    "driver license", "driving license", "водительские права", "права на байк", "права в таиланде",
    "открыть счет", "счет в банке", "карта банкомата", "открытие счета",
    "штамп", "консульство", "посольство", "паспорт", "загранпаспорт",
    # Rentals & Digest
    "#аренда", "сдам", "сниму", "аренда дома", "аренда виллы", "аренда кондо", "за последние сутки", "в чате обсуждали:"
]

GENERIC_TITLES = [
    "всем привет", "всем привет!", "добрый день", "здравствуйте", "здравствуйте!", "добрый вечер",
    "ребят, привет", "привет всем", "доброе утро", "локация", "интересное место", "вот такой",
    "вот здесь хорошо", "это да", "я нашла)", "спасибо", "отлично!)", "координаты", "точка на карте",
    "сегодня пятница", "я ищу магазины", "планируем приезд", "поделитесь контактами", "кто знает",
    "подскажите пожалуйста", "доброе утро друзья", "привет", "приветствую", "информация"
]

def extract_advanced_title(txt, loc_url):
    if not txt:
        return None

    # 1. 📍 Pin marker
    pin_match = re.search(r"📍\s*([^\n\r,\.\?]+)", txt)
    if pin_match:
        cand = pin_match.group(1).strip()
        cand = re.sub(r"#\w+", "", cand).strip()
        cand = re.sub(r"https?://\S+", "", cand).strip()
        if len(cand) >= 3 and not cand.lower().startswith("http") and cand.lower() not in GENERIC_TITLES:
            return cand

    # 2. Text with dash separator like "Sanpakoi Street Market — небольшой рынок"
    dash_match = re.search(r"^([A-Z0-9\s\'&\.-]{3,40})\s*[—–-]\s*", txt.strip(), re.MULTILINE)
    if dash_match:
        cand = dash_match.group(1).strip()
        if len(cand) >= 3 and cand.lower() not in GENERIC_TITLES:
            return cand

    # 3. AllTrails URL slug
    if "alltrails.com" in loc_url:
        at_match = re.search(r"alltrails\.com/trail/[^/\s]+/[^/\s]+/([a-z0-9-]+)", loc_url)
        if at_match:
            return at_match.group(1).replace("-", " ").title()

    # 4. Google Maps query parameter
    if loc_url:
        q_match = re.search(r"[?&]q=([^&\s]+)", loc_url)
        if q_match:
            val = urllib.parse.unquote(q_match.group(1)).replace("+", " ").strip()
            if val and not val.replace(".", "").isdigit() and len(val) > 2:
                return val

    # 5. English / Thai venue name inside lines
    eng_match = re.search(r"\b([A-Z][a-zA-Z0-9\s\'&]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|Bakery|Bar|Trail|Waterfall|Coworking|Hub|House|Villa|Hotel|Retreat|Farm))\b", txt)
    if eng_match:
        return eng_match.group(1).strip()

    # 6. Russian quoted name e.g. кафе "Имя"
    ru_quote = re.search(r'(?:кафе|ресторан|водопад|коворкинг|тропа|хайк|отель|бар)\s+["«]([^"»]+)["»]', txt, re.IGNORECASE)
    if ru_quote:
        return ru_quote.group(1).strip()

    # 7. First line if short & clean proper name
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    if lines:
        first = lines[0]
        cleaned = re.sub(r"^[^\w\s]+", "", first).strip()
        cleaned = re.sub(r"^\[.*?\]\s*", "", cleaned).strip()
        cleaned = re.sub(r"#\w+", "", cleaned).strip()
        
        lower_c = cleaned.lower()
        if (len(cleaned) >= 3 and len(cleaned) <= 50 
            and not any(g in lower_c for g in ["всем привет", "добрый день", "здравствуйте", "привет", "подскажите", "кто знает", "где ", "как ", "спасибо", "подсказать", "ребята", "пожалуйста", "ищу ", "мы ", "вы ", "кто ", "если "])
            and not cleaned.startswith("http")
            and not cleaned.startswith("www")):
            return cleaned

    return None

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM reviews")
reviews = c.fetchall()

found_titles = 0
missing_titles = 0

for r in reviews:
    txt = r["review_text"] or ""
    if any(k in txt.lower() for k in BLACK_KEYWORDS):
        continue
        
    t = extract_advanced_title(txt, r["source_link"] or "")
    if t:
        found_titles += 1
    else:
        missing_titles += 1

print(f"Total clean reviews inspected: {found_titles + missing_titles}")
print(f"Successfully extracted specific venue titles: {found_titles}")
print(f"Reviews without specific venue title: {missing_titles}")
