import json, re

posts = json.load(open('chiamgmaimy_posts.json'))
print(f"Total posts from @ChiamgMaimy: {len(posts)}")

# Test OmHome events in full history
omhome_events = []
for p in posts:
    txt = p['text']
    if ('omhome' in txt.lower() or 'om home' in txt.lower()) and any(k in txt.lower() for k in ["расписание", "распиание", "так же на этой неделе", "неделя творчества"]):
        parts = re.split(r'——+|(?=\b\d{1,2}/\d{2}\s*•)', txt)
        for part in parts:
            ptxt = part.strip()
            if len(ptxt) < 20: continue
            date_m = re.search(r'(\d{1,2}/\d{2}\s*•\s*[А-Яа-яA-Za-z]+\s*•\s*\d{1,2}:\d{2})', ptxt)
            title_m = re.search(r'(?:🍵|🎶|🫖|🎬|🎩|🪐|🧘|🌟)\s*([^\n\r]+)', ptxt)
            if title_m:
                t = title_m.group(1).strip()
                d_str = date_m.group(1).strip() if date_m else ""
                omhome_events.append((t, d_str))

print(f"Total OmHome events across 4 months: {len(omhome_events)}")
for e in omhome_events[:15]:
    print(" -", e[0], f"({e[1]})")
