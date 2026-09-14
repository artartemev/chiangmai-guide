import json, re

posts = json.load(open('chiamgmaimy_posts.json'))

food_posts = []
for p in posts:
    txt = p['text']
    first_line = txt.split('\n')[0].strip()
    if any(k in txt.lower() for k in ['кафе', 'кофейн', 'cafe', 'coffee', 'ресторан', 'пекарня', 'bakery', 'bistro', 'kitchen', 'vegan', 'веган', 'пицца', 'бургер', 'ramen', 'рамен', 'tea house', 'чайная']):
        if not any(r in txt.lower() for r in ['сколько стоит жить', 'аренда', 'виза', 'паспорт']):
            food_posts.append((p['id'], p['date'], first_line))

print(f"Total curated food spots from @ChiamgMaimy: {len(food_posts)}")
for fp in food_posts[:20]:
    print(f" - [{fp[1][:10]}] {fp[2][:70]}")
