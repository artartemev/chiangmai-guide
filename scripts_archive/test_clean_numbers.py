import json, re

CACHE_PATH = "maps_cache.json"
maps_cache = json.load(open(CACHE_PATH, encoding="utf-8"))

FOOD_KEYWORDS = [
    'cafe', 'coffee', 'restaurant', 'kitchen', 'bistro', 'bar', 'bakery', 'pizza',
    'ramen', 'noodle', 'tea', 'grill', 'vegan', 'vegetarian', 'eatery', 'diner',
    'brewers', 'roastery', 'food', 'burgers', 'gelato', 'steakhouse', 'sushi',
    'кафе', 'ресторан', 'кофейня', 'пекарня', 'пицца', 'рамен', 'еда', 'пиво', 'вино', 'чай', 'смузи', 'бургер'
]

EXCLUDE_KEYWORDS = [
    'condominium', 'condo', 'residence', 'apartment', 'hospital', 'clinic', 'dent', 'dental',
    'rent a car', 'driving school', 'massage', 'spa', 'sauna', 'gym', 'fitness',
    'motor', 'bike', 'repair', 'laundry', 'store', 'shop', 'market', 'farm', 'pier',
    'kayak', 'adventure', 'service', 'studio', 'church', 'school', 'optics', 'hotel'
]

NATURE_KEYWORDS = ['waterfall', 'national park', 'lake', 'viewpoint', 'водопад', 'озеро', 'смотровая', 'парк', 'peak']
WORKSPACE_KEYWORDS = ['coworking', 'коворкинг', 'yellow', 'punspace', 'work space']
HIKE_KEYWORDS = ['trail', 'тропа', 'hike', 'хайк', 'alltrails']

counts = {'cafe_restaurant': 0, 'nature': 0, 'hiking_trail': 0, 'workspace': 0, 'excluded': 0}

for u, val in maps_cache.items():
    p_name = val[0]
    if not p_name or p_name.replace('.', '').isdigit(): continue
    p_lower = p_name.lower()

    if any(k in p_lower for k in EXCLUDE_KEYWORDS):
        counts['excluded'] += 1
    elif any(k in p_lower for k in WORKSPACE_KEYWORDS):
        counts['workspace'] += 1
    elif any(k in p_lower for k in NATURE_KEYWORDS):
        counts['nature'] += 1
    elif any(k in p_lower for k in HIKE_KEYWORDS):
        counts['hiking_trail'] += 1
    elif any(k in p_lower for k in FOOD_KEYWORDS):
        counts['cafe_restaurant'] += 1
    else:
        counts['excluded'] += 1

print("Categorization of Google Maps Places in Cache:")
for cat, count in counts.items():
    print(f" - {cat}: {count}")
