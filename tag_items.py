"""
Derive sub-category tags for every place from its title, Google category and
description, so the UI can offer a second row of filters inside a category
(e.g. cafes → coffee / breakfast / thai / asian / european / bars / vegan).

Rules are ordered; an item can carry several tags. Results go to items.tags (JSON).
Usage: python3 tag_items.py
"""
import json
import re
import sqlite3

DB = "chiangmai_guide.db"

# category -> [(tag, regex over "title | google_category | description | summary")]
RULES = {
    "cafe_restaurant": [
        ("кофе", r"coffee|кофе|roaster|espresso|specialty|спешалти|tea house|чайн"),
        ("завтраки", r"breakfast|brunch|bakery|пекарн|завтрак|бранч|croissant|круассан|sourdough|bread"),
        ("тайская", r"\bthai\b|khao soi|kao soy|isan|исан|тайск|northern thai|север|khantoke|som tam|street food|уличн"),
        ("азия", r"japanese|sushi|ramen|izakaya|chinese|korean|vietnamese|burmese|indian|yunnan|dim sum|япон|суши|рамен|китай|корей|вьетнам|бирман|индий|юньнан|banh mi"),
        ("европа", r"pizza|pizzeria|italian|french|burger|steak|bbq|european|western|brasserie|diner|пицц|бургер|стейк|француз|италь|европ|барбекю"),
        ("бары", r"\bbar\b|\bpub\b|beer|craft|cocktail|jazz|nightlife|rooftop|sky bar|lounge|\bбар\b|пиво|крафт|коктейл|джаз|руфтоп|live music"),
        ("с видом", r"lake|view|garden|riverside|mountain|terrace|озер|с видом|сад\b|у реки|на крыше|терраса|jungle|джунгл"),
    ],
    "wellness": [
        ("массаж и спа", r"massage|spa\b|массаж|спа\b|bodywork|therap"),
        ("сауна и ice bath", r"sauna|ice bath|cold plunge|onsen|hot spring|bathhouse|сауна|онсен|источник|ледян|баня|steam|парн"),
        ("йога", r"yoga|pilates|meditation|йога|пилатес|медитац|shala|healing"),
        ("фитнес и бассейн", r"gym|fitness|pool|swim|бассейн|фитнес|sport|climb|скалодром|recovery|crossfit|muay|бокс"),
        ("красота", r"nail|lash|beauty|салон|hair|barber|wax|маникюр|ресниц|парикмах|skin|косметолог"),
    ],
    "services": [
        ("стоматологи", r"dental|dentist|стомат|smile"),
        ("ветеринары", r"animal|\bvet\b|veterinar|pet clinic|pet hospital|cat hotel|ветер|ветклиник"),
        ("врачи и госпитали", r"hospital|clinic|госпитал|клиник|medical|doctor|\bdr\.|врач|pediatric|педиатр|dermatolog|ent\b|eye|психиатр|psychiatr|lab test|анализ|acupuncture"),
        ("прокат", r"rental|rent a|прокат|аренд|bike|motor|scooter|car rental|wheels"),
        ("визы и документы", r"immigration|иммигр|border|driving school|автошкол|dlt|visa|виз[аы]"),
        ("красота", r"nail|lash|beauty|салон|barber|hair|маникюр|парикмах"),
        ("воркшопы", r"workshop|studio|craft|class|мастер-класс|воркшоп|pottery|керамик|paint|jewelry|art center"),
        ("магазины", r"\bshop\b|store|mall|market|магазин|молл|gift"),
    ],
    "nature": [
        ("водопады", r"waterfall|водопад"),
        ("озёра", r"lake|reservoir|\bdam\b|озер|водохран|дамб|плотин"),
        ("смотровые и горы", r"viewpoint|peak|summit|\bdoi\b|mountain|ridge|смотров|вершин|гор[аы]\b|panoram|cloud"),
        ("парки и сады", r"\bpark\b|garden|farm|orchard|plantation|zoo|парк|сад\b|ферм|плантац|зоопарк|botanical"),
        ("храмы", r"\bwat\b|temple|shrine|pagoda|храм|пагод|buddh|monk"),
        ("пещеры и источники", r"cave|пещер|hot spring|источник|canyon|каньон"),
    ],
    "hiking_trail": [
        ("тропы", r"."),
    ],
    "stay": [
        ("отели", r"hotel|hostel|guesthouse|отель|хостел|гест"),
        ("кондо и квартиры", r"condo|apartment|кондо|апарт|квартир|studio"),
        ("глэмпинги и кемпинг", r"camp|glamp|homestay|tent|кемпинг|глэмп|хоумстей|палатк|treehouse|дом на дереве"),
        ("резорты и виллы", r"resort|villa|lodge|retreat|резорт|вилл|ретрит|pool villa"),
    ],
    "workspace": [
        ("коворкинги", r"."),
    ],
    "kids": [
        ("животные и фермы", r"zoo|animal|farm|bunny|safari|deer|зоопарк|животн|ферм|кролик|олен|капибар|пони|птиц|рыб"),
        ("игровые и парки", r"play|park|playground|water park|canyon|игров|площадк|парк|аквапарк|батут"),
        ("кафе с детьми", r"cafe|restaurant|bistro|еда|кафе|ресторан"),
        ("развитие и творчество", r"museum|art|science|astropark|workshop|музей|наук|планетарий|мастер-класс|творчеств|картинг|circuit"),
        ("детское здоровье", r"pediatric|clinic|педиатр|клиник|врач"),
    ],
}


def tags_for(category, text, veg):
    tags = [tag for tag, rx in RULES.get(category, []) if re.search(rx, text, re.I)]
    if category == "cafe_restaurant" and veg:
        tags.append("веган")
    if category == "nature" and not tags:
        tags.append("парки и сады")
    return tags


def main():
    conn = sqlite3.connect(DB)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(items)")}
    if "tags" not in cols:
        conn.execute("ALTER TABLE items ADD COLUMN tags TEXT DEFAULT '[]'")
    rows = conn.execute("SELECT id, category, title, google_category, description, community_summary, veg_friendly FROM items").fetchall()
    stats = {}
    for iid, cat, title, gcat, desc, summ, veg in rows:
        text = " | ".join(str(x or "") for x in (title, gcat, desc, summ))
        tags = tags_for(cat, text, veg)
        conn.execute("UPDATE items SET tags = ? WHERE id = ?", (json.dumps(tags, ensure_ascii=False), iid))
        for t in tags:
            stats[(cat, t)] = stats.get((cat, t), 0) + 1
    conn.commit()
    for (cat, t), n in sorted(stats.items()):
        print(f"{cat:16s} {t:22s} {n}")
    print("untagged:", conn.execute("SELECT count(*) FROM items WHERE tags = '[]' AND category != 'event'").fetchone()[0])


if __name__ == "__main__":
    main()
