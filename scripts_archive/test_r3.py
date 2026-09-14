import json, re

p = '/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/result 3.json'
d = json.load(open(p, encoding='utf-8'))
msgs = d.get('messages', [])
print(f"Total messages in result 3.json: {len(msgs)}")

def extract_text(obj):
    if isinstance(obj, str): return obj
    elif isinstance(obj, list): return "".join([extract_text(item) for item in obj])
    elif isinstance(obj, dict):
        if "text" in obj: return extract_text(obj["text"])
        elif "content" in obj: return extract_text(obj["content"])
    return ""

maps_links = []
events = []
food_posts = []

for m in msgs:
    txt = extract_text(m.get('text', '')).strip()
    if not txt or len(txt) < 15: continue

    m_match = re.search(r"https?://[\w\.-]*(?:google\.com/maps|maps\.app\.goo\.gl|goo\.gl/maps)[^\s,\)\"\']*", txt)
    if m_match:
        maps_links.append(m_match.group(0))

    txt_lower = txt.lower()
    if any(k in txt_lower for k in ['omhome', 'om home', 'фестиваль', 'концерт', 'live concert', 'blues night', 'workshop', 'воркшоп', 'fair 2026', 'fest 2026', 'расписание']):
        events.append(txt[:80].replace('\n', ' '))
    elif any(k in txt_lower for k in ['кафе', 'кофейн', 'cafe', 'coffee', 'ресторан', 'пекарня', 'bakery', 'bistro', 'kitchen', 'vegan']):
        food_posts.append(txt[:80].replace('\n', ' '))

print(f"Google Maps links in result 3.json: {len(maps_links)}")
print(f"Event mentions: {len(events)}")
print(f"Food mentions: {len(food_posts)}")
