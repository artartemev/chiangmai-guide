import json
import re

posts = json.load(open('chiamgmaimy_posts.json', encoding='utf-8'))
print(f"Loaded {len(posts)} posts from @ChiamgMaimy")

curated_items = []

for p in posts:
    txt = p['text'].strip()
    p_id = p['id']
    p_date = p['date']
    link = f"https://t.me/ChiamgMaimy/{p_id}"

    # Check OmHome multi-event schedule
    if ("omhome" in txt.lower() or "om home" in txt.lower()) and any(k in txt.lower() for k in ["расписание", "распиание", "так же на этой неделе"]):
        # Split by sub-events
        parts = re.split(r'——+|(?=\b\d{1,2}/\d{2}\s*•)', txt)
        for part in parts:
            ptxt = part.strip()
            if not ptxt or len(ptxt) < 25:
                continue
            date_m = re.search(r'(\d{1,2}/\d{2}\s*•\s*[А-Яа-яA-Za-z]+\s*•\s*\d{1,2}:\d{2})', ptxt)
            title_m = re.search(r'(?:🍵|🎶|🫖|🎬|🎩|🪐|🧘|🌟)\s*([^\n\r]+)', ptxt)
            if not title_m:
                lines = [l.strip() for l in ptxt.split('\n') if l.strip()]
                for l in lines[1:]:
                    if len(l) > 3 and not l.startswith('💰') and not l.startswith('✍️'):
                        title_m = re.match(r'^([^\n\r]+)', l)
                        break
            if title_m:
                t = title_m.group(1).strip()
                t = re.sub(r'^[^\w\s"«]+', '', t).strip()
                d_str = date_m.group(1).strip() if date_m else ""
                curated_items.append({
                    "title": t,
                    "venue_name": "OmHome Space",
                    "category": "event",
                    "neighborhood": "Pa Daet / Chang Khlan",
                    "location_url": "https://maps.app.goo.gl/FcH2vP9WtEEJqSM48",
                    "event_date": d_str,
                    "description": ptxt[:350],
                    "source_link": link,
                    "msg_id": p_id
                })
        continue

    # Single event posts
    is_event = False
    if any(k in txt.lower() for k in ['фестиваль', 'концерт', 'live concert', 'blues night', 'workshop', 'воркшоп', 'fair 2026', 'fest 2026', 'вечеринка', 'ярмарка', 'выставка']):
        if not any(r in txt.lower() for r in ['сколько стоит жить', 'как на концерте', 'отзыв']):
            is_event = True

    if is_event:
        lines = [l.strip() for l in txt.split('\n') if l.strip()]
        cand_title = re.sub(r'^[^\w\s"«]+', '', lines[0]).strip()
        cand_title = re.sub(r'^(?:🎶|🌿|🔥|🎸|☕️|🍸|🌲|🎨|🎧|🎷|🎬|🍜|🏃‍♀️|🥑|🍲)\s*', '', cand_title).strip()
        
        # Look for venue
        venue = ""
        v_m = re.search(r'(?:📍|в|at|@)\s*([A-Z][a-zA-Z0-9\s"\'&-]{2,35}(?:Cafe|Bistro|Coffee|Restaurant|Kitchen|Resort|Park|Market|Studio|School|House|Villa|Hotel|Home|Club|Cocoon|MAIIAM))\b', txt)
        if v_m:
            venue = v_m.group(1).strip()

        # Date
        date_m = re.search(r'\b(\d{1,2}(?:[–-]\d{1,2})?\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|сент|окт|ноя|дек|\.\d{2}))', txt, re.IGNORECASE)
        d_str = date_m.group(1).strip() if date_m else ""

        if len(cand_title) >= 5 and len(cand_title) <= 60 and not cand_title.endswith('?'):
            curated_items.append({
                "title": cand_title,
                "venue_name": venue or "Chiang Mai",
                "category": "event",
                "neighborhood": "Other",
                "location_url": "",
                "event_date": d_str,
                "description": txt[:350],
                "source_link": link,
                "msg_id": p_id
            })

print(f"Extracted {len(curated_items)} high quality events from @ChiamgMaimy:")
for it in curated_items[:12]:
    print(f" - [{it['category'].upper()}] {it['title']} @ {it['venue_name']} ({it['event_date'] or 'No date'}) -> {it['neighborhood']}")
