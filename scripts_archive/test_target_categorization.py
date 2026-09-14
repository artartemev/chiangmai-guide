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
        mm = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", t)
        if mm:
            links.append((mm.group(0).rstrip(".,)"), t[:150]))
    return links

r3_links = get_links(p3)
r4_links = get_links(p4)
r5_links = get_links(p5)

# Calculate chat mentions
chat_mentions = {}
for u, txt in r4_links + r5_links:
    clean_u = u.split("?g_st=")[0]
    chat_mentions[clean_u] = chat_mentions.get(clean_u, 0) + 1

r3_unique = set(u.split("?g_st=")[0] for u, txt in r3_links)

CATEGORIES = {
    'cafe_restaurant': ['cafe', 'coffee', 'restaurant', 'kitchen', 'bistro', 'bar', 'bakery', 'pizza', 'ramen', 'noodle', 'tea', 'grill', 'vegan', 'vegetarian', 'eatery', 'diner', 'brewers', 'roastery', 'food', 'бургер', 'кафе', 'ресторан', 'кофейня', 'пекарня', 'пицца', 'бар', 'чайная', 'рамен', 'gelato'],
    'nature': ['waterfall', 'national park', 'lake', 'viewpoint', 'водопад', 'озеро', 'смотровая', 'каньон', 'canyon', 'cave', 'пещера'],
    'hiking_trail': ['trail', 'тропа', 'hike', 'хайк', 'alltrails'],
    'workspace': ['coworking', 'коворкинг', 'yellow', 'punspace', 'work space', 'the story 106', 'camp maya'],
    'wellness': ['massage', 'spa', 'sauna', 'hot spring', 'массаж', 'спа', 'сауна', 'горячие источники', 'yoga', 'йога'],
    'stay': ['hotel', 'resort', 'villa', 'condominium', 'condo', 'отель', 'резорт', 'вилла', 'хостел', 'hostel', 'apartment'],
    'services': ['clinic', 'hospital', 'dent', 'dental', 'driving school', 'rent a car', 'laundry', 'motor', 'bike', 'repair', 'больниц', 'клиник', 'стоматолог', 'автошкол', 'прачечн']
}

classified = {cat: [] for cat in CATEGORIES}

# Process candidates: all r3 places + chat places with 2+ mentions
all_candidates = set(list(r3_unique) + [u for u, cnt in chat_mentions.items() if cnt >= 2])

for u in all_candidates:
    entry = maps_cache.get(u)
    if not entry:
        clean_u = u.split("?g_st=")[0]
        entry = maps_cache.get(clean_u)
    if not entry or not entry[0] or entry[0].replace('.', '').isdigit():
        continue
    name = entry[0]
    p_lower = (name + " " + entry[2]).lower()

    matched_cat = None
    for cat, keywords in CATEGORIES.items():
        if any(k in p_lower for k in keywords):
            matched_cat = cat
            break
    if matched_cat:
        classified[matched_cat].append((name, entry[1], u))

print("Classified curated places:")
for cat, items in classified.items():
    print(f" - {cat}: {len(items)} places")
