import json, re

p3 = '/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/result 3.json'
p4 = '/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/result 4.json'
p5 = '/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/result 5.json'
maps_cache = json.load(open('maps_cache.json', encoding='utf-8'))

def extract_text(obj):
    if isinstance(obj, str): return obj
    elif isinstance(obj, list): return "".join([extract_text(item) for item in obj])
    elif isinstance(obj, dict):
        if "text" in obj: return extract_text(obj["text"])
        elif "content" in obj: return extract_text(obj["content"])
    return ""

def get_links(fpath):
    d = json.load(open(fpath, encoding='utf-8'))
    links = []
    for m in d.get('messages', []):
        t = extract_text(m.get('text', ''))
        m_m = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", t)
        if m_m:
            links.append((m_m.group(0).rstrip(".,)"), t[:100]))
    return links

r3_links = get_links(p3)
r4_links = get_links(p4)
r5_links = get_links(p5)

print(f"Maps links in result 3 (Мой Чиангмай): {len(r3_links)}")
print(f"Maps links in result 4 (Треккинг): {len(r4_links)}")
print(f"Maps links in result 5 (Чат): {len(r5_links)}")

# Count mentions in chat
chat_mentions = {}
for u, txt in r5_links + r4_links:
    clean_u = u.split("?g_st=")[0]
    chat_mentions[clean_u] = chat_mentions.get(clean_u, 0) + 1

r3_unique_urls = set(u.split("?g_st=")[0] for u, txt in r3_links)

# Categorize
FOOD_KEYWORDS = ['cafe', 'coffee', 'restaurant', 'kitchen', 'bistro', 'bar', 'bakery', 'pizza', 'ramen', 'noodle', 'tea', 'grill', 'vegan', 'vegetarian', 'eatery', 'diner', 'brewers', 'roastery', 'кафе', 'ресторан', 'кофейня', 'пекарня', 'пицца', 'бар']
NATURE_KEYWORDS = ['waterfall', 'national park', 'lake', 'viewpoint', 'водопад', 'озеро', 'смотровая', 'парк', 'peak']
HIKE_KEYWORDS = ['trail', 'тропа', 'hike', 'хайк', 'alltrails']
SERVICE_KEYWORDS = ['clinic', 'hospital', 'dent', 'dental', 'driving school', 'rent a car', 'laundry', 'massage', 'spa', 'motor', 'bike', 'repair', 'больниц', 'клиник', 'стоматолог', 'автошкол', 'массаж', 'прачечн']

counts = {'cafe_restaurant': 0, 'nature': 0, 'hiking_trail': 0, 'services': 0, 'workspace': 0}

for u in set(list(r3_unique_urls) + [u for u, cnt in chat_mentions.items() if cnt >= 2]):
    entry = maps_cache.get(u)
    if not entry or not entry[0] or entry[0].replace('.', '').isdigit(): continue
    p_name = entry[0].lower()
    
    if any(k in p_name for k in SERVICE_KEYWORDS):
        counts['services'] += 1
    elif any(k in p_name for k in ['coworking', 'коворкинг', 'yellow', 'punspace']):
        counts['workspace'] += 1
    elif any(k in p_name for k in NATURE_KEYWORDS):
        counts['nature'] += 1
    elif any(k in p_name for k in HIKE_KEYWORDS):
        counts['hiking_trail'] += 1
    elif any(k in p_name for k in FOOD_KEYWORDS):
        counts['cafe_restaurant'] += 1

print("\nCurated Counts (Channel + Chat 2+ mentions):")
for c, cnt in counts.items():
    print(f" - {c}: {cnt}")
