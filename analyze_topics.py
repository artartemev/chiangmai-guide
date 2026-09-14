import json
import collections
import re
from itertools import islice

# Let's read the main chat (result 5.json) and look for questions
def extract_questions():
    questions = []
    try:
        with open('../result 5.json', 'r') as f:
            data = json.load(f)
            for msg in data.get('messages', []):
                text = msg.get('text', '')
                if isinstance(text, list):
                    text = ' '.join([t.get('text', '') if isinstance(t, dict) else t for t in text])
                if not isinstance(text, str): continue
                
                text = text.lower()
                if '?' in text or 'подскажите' in text or 'кто знает' in text or 'посоветуйте' in text:
                    questions.append(text)
    except Exception as e:
        print("Error:", e)
    return questions

questions = extract_questions()
print(f"Found {len(questions)} question messages.")

# Simple keyword frequency for common Chiang Mai expat topics
keywords = {
    'Визы / Бордерраны': ['виз', 'бордер', 'border', 'dtv', 'ed visa', 'штамп', 'продлен', 'имигрейшн', 'иммигрейшн'],
    'Байки / Транспорт': ['байк', 'мопед', 'скутер', 'аренд', 'права', 'штраф', 'гаи', 'полиц', 'бензин'],
    'Жилье / Кондо': ['кондо', 'аренд', 'жиль', 'квартир', 'дом', 'депозит', 'контракт', 'коммунал', 'счет', 'электричеств'],
    'Медицина / Страховка': ['врач', 'больниц', 'госпитал', 'клиник', 'страховк', 'стоматолог', 'зуб', 'аптек', 'лекарств', 'прививк'],
    'Деньги / Банки': ['банк', 'карт', 'счет', 'бангкок банк', 'обмен', 'крипт', 'наличн', 'банкомат', 'перевод', 'рубл'],
    'Связь / Интернет': ['сим', 'интернет', 'провайдер', 'ais', 'true', 'dtac', 'связь', 'роутер', 'wifi'],
    'Документы (TM30, Резидентка)': ['tm30', 'тм30', 'тм 30', 'резидент', 'certificate of residence', 'сертификат'],
    'Еда / Доставка': ['еда', 'кафе', 'ресторан', 'доставк', 'grab', 'foodpanda', 'продукты', 'рынок', 'макро', 'makro'],
    'Сезон дыма (Burning Season)': ['дым', 'смог', 'pm 2.5', 'pm2.5', 'сезон', 'воздух', 'очиститель', 'фильтр', 'маск'],
    'Покупки / Шопинг': ['купить', 'магазин', 'lazada', 'shopee', 'торговый', 'централ', 'фестиваль', 'одежд', 'обувь'],
    'Спорт / Фитнес': ['зал', 'фитнес', 'тренажер', 'бассейн', 'йог', 'спорт', 'теннис', 'муай', 'тайский бокс'],
    'Дети / Школы': ['дет', 'школ', 'сад', 'нян', 'ребен', 'кружок'],
    'Визаран / Лаос / Мьянма': ['лаос', 'мьянм', 'визаран', 'посольств', 'консульств'],
    'Животные / Ветклиники': ['собак', 'кошк', 'кот', 'вет', 'клиник', 'корм', 'перелет'],
}

counts = collections.defaultdict(int)
for q in questions:
    for topic, words in keywords.items():
        if any(w in q for w in words):
            counts[topic] += 1

for topic, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{topic}: {count}")

