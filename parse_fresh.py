import json
import re
from collections import Counter

files = ['../result.json', '../result 2.json', '../result 3.json', '../result 4.json', '../result 5.json']
found_places = []
links = Counter()

for fpath in files:
    try:
        with open(fpath, 'r') as f:
            data = json.load(f)
            # just read the last 5000 messages of each file
            messages = data.get('messages', [])[-5000:]
            for msg in messages:
                text = msg.get('text', '')
                if isinstance(text, list):
                    text = ' '.join([t.get('text', '') if isinstance(t, dict) else t for t in text])
                if not isinstance(text, str): continue
                
                urls = re.findall(r'(https://maps\.app\.goo\.gl/[a-zA-Z0-9]+)', text)
                for u in urls:
                    links[u] += 1
                    if links[u] == 1:
                        found_places.append((u, text[:200]))
    except Exception as e:
        print(f"Error {fpath}: {e}")

for link, count in links.most_common(5):
    ctx = next((t for l, t in found_places if l == link), "")
    print(f"{count} mentions: {link}\nContext: {ctx}\n")

