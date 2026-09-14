import json
import os
import re

search_queries = ["дима", "дмитрий", "dima", "dmitry", "dmitriy"]
dimas = {}

print("Reading result.json...")
try:
    with open('../result.json', 'r') as f:
        data = json.load(f)
        
    for msg in data.get('messages', []):
        sender = msg.get('from')
        if not sender: continue
        
        name_lower = sender.lower()
        if any(q in name_lower for q in search_queries):
            user_id = msg.get('from_id')
            if user_id not in dimas:
                dimas[user_id] = sender
except Exception as e:
    print("Error:", e)

print(f"Found {len(dimas)} unique Dimas in JSON export.")
