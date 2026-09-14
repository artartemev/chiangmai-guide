import json
import re
import requests
import urllib.request
from datetime import datetime

LM_STUDIO_URL = "http://192.168.1.35:1143/v1/chat/completions"
MODEL_NAME = "prism-ml/bonsai-27b"
TIMEOUT_SEC = 60

NEIGHBORHOODS = ["Nimman", "Old City", "Hang Dong", "Mae Rim", "Mae On", "San Sai", "Santitham", "Chang Phueak", "Jed Yod", "Doi Suthep", "Mae Kampong"]

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

SYSTEM_PROMPT = """You are an expert AI curator for Chiang Mai, Thailand.
You are analyzing Telegram chat messages. Messages are often conversational (e.g. Q&A, replies to previous questions, recommendations with links).

CRITICAL RULE: DO NOT extract document guides, yellow tabien baan house registrations, visa discussions, DTV visa procedures, work permits, bank account guides, or housing rental ads. Return {"has_entity": false} for these.

Return valid JSON matching this schema:
{
  "has_entity": true,
  "category": "cafe_restaurant" | "workspace" | "nature" | "hiking_trail" | "event",
  "dietary_type": "vegan" | "vegetarian" | "omnivore" | "coffee_only" | "none",
  "neighborhood": "Nimman" | "Old City" | "Hang Dong" | "Mae Rim" | "Mae On" | "Santitham" | "Doi Suthep" | "Other",
  "title": "Exact Clean Name of Place, Cafe, Restaurant, Spot, Trail or Event (e.g. 'TYRA — Japanese Tapas Bar', 'Goodsouls Kitchen', 'Monk's Trail'). DO NOT use chat greetings like 'Всем привет' or questions.",
  "description": "Concise Russian summary explaining what this place is, user recommendation, features, hours, prices",
  "location_url": "Google Maps URL if present or empty string",
  "event_date": "YYYY-MM-DD if event date is mentioned or empty string"
}

If it is general chat or visa/document discussion, return {"has_entity": false}.
DO NOT return markdown fences. Return JSON only."""

def fetch_link_info(text):
    urls = re.findall(r"https?://[^\s]+", text)
    if not urls:
        return ""
    info = []
    for u in urls[:2]:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                final_u = resp.geturl()
                html = resp.read(8000).decode("utf-8", errors="ignore")
                t_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
                if t_match:
                    title_str = t_match.group(1).strip()
                    info.append(f"Ссылка ({final_u}): {title_str}")
        except Exception:
            pass
    return "\n".join(info)

def extract_with_llm(text, reply_context=""):
    if not text or len(text) < 10:
        return {"has_entity": False}
        
    lower = text.lower()
    if any(k in lower for k in VISA_AND_NOISE_KEYWORDS):
        return {"has_entity": False}
        
    link_meta = fetch_link_info(text)
    
    full_input = ""
    if reply_context:
        full_input += f"[Контекст диалога / Вопрос]:\n{reply_context}\n\n"
    full_input += f"[Основное сообщение / Ответ]:\n{text}"
    if link_meta:
        full_input += f"\n\n[Информация со страницы ссылки]:\n{link_meta}"
        
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_input}
        ],
        "temperature": 0.1
    }
    
    try:
        resp = requests.post(LM_STUDIO_URL, json=payload, timeout=TIMEOUT_SEC)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            res = json.loads(content)
            if isinstance(res, dict) and "has_entity" in res:
                if any(k in (res.get("title", "") or "").lower() for k in VISA_AND_NOISE_KEYWORDS):
                    return {"has_entity": False}
                return res
    except Exception:
        pass
        
    return extract_with_rules(text)

def extract_with_rules(text):
    lower = text.lower()
    if any(k in lower for k in VISA_AND_NOISE_KEYWORDS):
        return {"has_entity": False}

    maps_match = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl)[^\s]*", text)
    location_url = maps_match.group(0) if maps_match else ""
    
    category = None
    dietary = "none"
    
    if any(k in lower for k in ["коворкинг", "coworking", "рабоч space", "hub", "yellow coworking", "punspace"]):
        category = "workspace"
    elif any(k in lower for k in ["водопад", "waterfall", "каньон", "слоны", "слон", "озеро", "гора", "nature", "дои интанон", "viewpoint"]):
        category = "nature"
    elif any(k in lower for k in ["хайк", "хайкинг", "трек", "тропа", "trail", "hike", "hiking", "monk trail"]):
        category = "hiking_trail"
    elif any(k in lower for k in ["митап", "ивент", "фестиваль", "концерт", "вечеринка", "event", "meetup", "party"]):
        category = "event"
    elif any(k in lower for k in ["веган", "vegan", "вегетариан", "вег ", "кофе", "кафе", "ресторан", "пицца", "суши", "том ям", "breakfast", "bakery", "coffee", "cafe", "restaurant", "matcha"]):
        category = "cafe_restaurant"
        if "веган" in lower or "vegan" in lower:
            dietary = "vegan"
        elif "вегетариан" in lower or "vegetarian" in lower:
            dietary = "vegetarian"
        elif "кофе" in lower or "coffee" in lower:
            dietary = "coffee_only"
        else:
            dietary = "omnivore"
            
    if not category:
        return {"has_entity": False}
        
    neighborhood = "Other"
    for n in NEIGHBORHOODS:
        if n.lower() in lower:
            neighborhood = n
            break
            
    event_date = ""
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if date_match:
        event_date = date_match.group(1)
        
    title = ""
    pin_match = re.search(r"📍\s*([^\n\r,\.\?]+)", text)
    if pin_match:
        title = pin_match.group(1).strip()
    else:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines:
            cleaned = re.sub(r"^\[.*?\]\s*", "", line)
            cleaned = re.sub(r"^.*?:\s*", "", cleaned)
            if len(cleaned) > 3 and len(cleaned) < 50 and not cleaned.startswith("(") and not cleaned.startswith("http"):
                title = cleaned.strip()
                break
            
    if not title:
        return {"has_entity": False}

    return {
        "has_entity": True,
        "category": category,
        "dietary_type": dietary,
        "neighborhood": neighborhood,
        "title": title,
        "description": text[:300].strip(),
        "location_url": location_url,
        "event_date": event_date
    }
