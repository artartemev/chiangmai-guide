"""
Seed routes (ordered day plans) and collections (thematic lists) into the DB.
Idempotent: a collection with the same title is replaced. Item ids reference
the `items` table; a missing id is skipped with a warning.

Usage: python3 seed_collections.py
"""
import sqlite3

DB = "chiangmai_guide.db"

ROUTES = [
    {
        "title": "Дой Интанон за один день",
        "description": "Самая высокая точка Таиланда: водопад, тропа над облаками, королевские пагоды и деревня Мэ Кланг Луанг. Выезжайте не позже 7 утра.",
        "duration": "Весь день", "transport": "Авто или байк, 1.5–2 ч от города", "budget": "300 ฿ вход в парк + еда", "cover": 176,
        "items": [
            (180, "Первая остановка по дороге наверх: мощный водопад Вачиратхан, 10 минут от парковки."),
            (179, "Кью Мэ Пан — кольцевая тропа 3 км по гребню над облаками. С ноября по май только с местным гидом (200 ฿ на группу)."),
            (176, "Две королевские пагоды и сады. Лучший свет — до полудня, потом наползают облака."),
            (320, "На обратном пути: тропа Пха Док Сиео через рисовые террасы и кофейные плантации, финиш в деревне с обедом."),
            (178, "Если хочется остаться на ночь: хоумстей и кемпинг на склоне, рассвет над долиной."),
        ],
    },
    {
        "title": "Чиангдао: горы, источники и ночь в кемпинге",
        "description": "Второй по популярности выезд после Интанона. Час с небольшим на север — и другой климат, известняковая гора Дой Луанг и горячие источники в лесу.",
        "duration": "1–2 дня", "transport": "Байк или авто, 75 км от города", "budget": "$$", "cover": 262,
        "items": [
            (139, "По дороге: горячий источник Понг Дуэт с гейзером в лесу. Утром почти нет людей."),
            (262, "Смотровая на Дой Луанг Чиангдао — главный вид региона, особенно на закате и рассвете."),
            (338, "Заповедник у подножия горы: лёгкая прогулка, птицы, бабочки."),
            (293, "Понг Анг — природные горячие ванны, можно приехать вечером и отмокать под звёздами."),
            ("https://maps.app.goo.gl/ZehQgSH1mR67RyCh9", "Ночёвка: Cocoa Camp Chiang Dao из списка глэмпингов чата, палатки с видом на гору."),
        ],
    },
    {
        "title": "Мэ Рим и Мон Чам на выходные",
        "description": "Ближайший «горный» выезд: озеро с бамбуковыми хижинами, кофейная плантация, смотровые Мон Чама и онсен на обратном пути.",
        "duration": "1 день или ночёвка", "transport": "Байк, 30–50 км", "budget": "$$", "cover": 303,
        "items": [
            (303, "Хуай Тынг Тао: озеро с хижинами над водой, завтрак с видом. Вход 50 ฿."),
            (120, "Кофейная плантация Doi Chaang — кофе, парк и прогулка среди деревьев."),
            (300, "Смотровая Панг Хва и апельсиновые сады Мон Чама — фото-точка номер один."),
            ("https://maps.app.goo.gl/dQGPa85RVHvuCty97", "Ночёвка в глэмпинге The Doi Moncham (из списка чата) — палатки с видом на долину."),
            (256, "На обратном пути: японский онсен на Мон Чаме, идеальное завершение дня."),
        ],
    },
    {
        "title": "Горячие источники Сан Кампхэнг и Мэ Кампонг",
        "description": "Маршрут на восток от города: онсен, деревня в горах, водопад и пицца из дровяной печи по дороге домой.",
        "duration": "Полдня — день", "transport": "Байк или авто, 40–50 км", "budget": "$$", "cover": 476,
        "items": [
            (476, "Waree Onsen — самый ухоженный из горячих источников региона, приватные ванны."),
            (339, "Водопад Мэ Кампонг и одноимённая горная деревня — прохлада и кофе на террасах."),
            (74, "The Stove Mae On — пицца из дровяной печи по дороге обратно."),
            (163, "Green Moon — тихое кафе-бистро в Сан Кампхэнге, если ещё есть силы."),
        ],
    },
    {
        "title": "Пятница вечером: крафт, джаз и рок",
        "description": "Классический вечер в Старом городе по рекомендациям чата: пиво, джем-сейшн у Северных ворот и рок до поздна.",
        "duration": "Вечер", "transport": "Пешком по Старому городу", "budget": "$$", "cover": 77,
        "items": [
            (357, "Начать с Renegade — крупнейшая карта крафтового пива в городе, бургеры и пицца."),
            (77, "North Gate Jazz Co-Op — легендарный джем каждый вторник, но живая музыка есть ежедневно. Приходите к 21:00, места заканчиваются."),
            (192, "Thapae East — концерты, театр и арт-пространство, смотрите афишу."),
            (362, "Crossroad Rock Bar — живой рок, если вечер только начинается."),
        ],
    },
    {
        "title": "Завтрак и кофе в Старом городе",
        "description": "Утренний маршрут пешком: французская пекарня, сауэрдоу, спешалти и веганский бранч — всё в квадрате Старого города.",
        "duration": "Утро", "transport": "Пешком", "budget": "$", "cover": 355,
        "items": [
            (355, "Chouquette — круассаны и французская выпечка, самый упоминаемый завтрак в чате."),
            (95, "Phin & Feta — кофе и хлеб на закваске, маленькое место, лучше пораньше."),
            (217, "Zohng Coffee — большая тихая кофейня, можно поработать."),
            (60, "Goodsouls Kitchen — веганский бранч и безглютеновые опции, стабильно быстрый Wi-Fi."),
        ],
    },
]

COLLECTIONS = [
    {
        "title": "Чиангмай с детьми",
        "description": "Контактные мини-зоопарки, кафе с игровыми зонами, аквапарки, планетарий, ночное сафари, парки и проверенные педиатры — подборка из рекомендаций сообщества.",
        "cover": 578,
        "items": [
            (578, "Lanna Mini Zoo — пони, альпаки, капибары, гигантские черепахи и просторное кафе."),
            (182, "Blink me Bunny — кафе-кемпинг на открытом воздухе, кролики, утки, олени."),
            (79, "Le Petit Zoo — контактный зоопарк в Мае Рим: капибары и сурикаты."),
            (579, "Lenmaii Playground & Cafe — большая детская игровая площадка, ролевые зоны, мастер-классы."),
            (585, "Princess Sirindhorn AstroPark (NARIT) — интерактивный музей науки и цифровой купольный планетарий."),
            (586, "Chiang Mai Night Safari — сафари-трамвайчики по саванне, лазерное шоу у озера."),
            (574, "Chada Cafe — семейное кафе с детской площадкой, садом и животными."),
            (575, "Choeng Doi Suthep — станция спасения диких животных, комфортная тенистая тропа и олени."),
            (576, "Pan's Farm — свежая фермерская еда, мини-ферма и площадка на свежем воздухе."),
            (577, "Uncle Pong Mini Zoo — загородный мини-зоопарк и кафе, кормление козочек."),
            (582, "Baan Tawai Prawn Fishing — ловля креветок всей семьей, улов жарят на гриле."),
            (583, "99 Villa & Cafe — карликовые свинки, кролики, ручей и десерты."),
            (584, "Baan Jang Nak — уникальный музей деревянной скульптуры слонов."),
            (418, "Grand Canyon Water Park — надувной аквапарк на карьере, детям от 6 лет."),
            (313, "Зоопарк Чиангмая с аквариумом и трамвайчиками."),
            (61, "Парк PAO — большой зелёный парк с площадками, лучший для прогулок с малышами."),
            (119, "Буак Хард — парк в Старом городе, пруд с рыбами и площадка."),
            (97, "Ma Plearn — семейное wellness-пространство с занятиями для детей."),
            (221, "Dr. Artima — педиатр и семейный врач."),
            (232, "Dr. Pui — педиатр."),
        ],
    },
    {
        "title": "Купаться: водопады и озёра",
        "description": "Куда ехать в жару. От «липкого» водопада в 40 минутах до дамб и озёр с кемпингом. В сезон дождей (июль–октябрь) вода мутная и течение сильное — смотрите по погоде.",
        "cover": 334,
        "items": [
            (334, "Sticky Waterfalls — по известняку можно ходить босиком прямо по воде. Самый популярный."),
            (180, "Вачиратхан — самый мощный водопад Интанона, купаться нельзя, но брызги долетают."),
            (395, "Мок Фа — купаться можно, по дороге в Пай."),
            (303, "Озеро Хуай Тынг Тао — бамбуковые хижины, еда, купание."),
            (344, "Озеро CMU — бег, закаты, студенческая атмосфера."),
            (246, "Дамба Мэ Нгат — плавучие дома и лодки на целый день."),
            (339, "Водопад Мэ Кампонг — прохлада и горная деревня."),
            (325, "Хуай Кэу — водопад у подножия Дой Сутеп, 10 минут от Нимана."),
            (414, "Мэ Я — 260-метровый каскад на Интаноне, меньше людей."),
            (452, "Тат Мок — тихий водопад в Мэ Риме."),
            (440, "Дамба Мэ Куанг — смотровая и озеро."),
        ],
    },
    {
        "title": "Recovery: сауны, ice bath и онсены",
        "description": "Одна из самых горячих тем чата в 2025–2026. Корейская баня, финские сауны с ледяными ваннами, японские онсены.",
        "cover": 242,
        "items": [
            (242, "K-Sauna — корейская баня с чимчильбаном, самая обсуждаемая."),
            (98, "Eudemonia — сауна и ice bath в Ханг Донге."),
            (282, "JT Forest — лесная сауна и cold plunge."),
            (278, "Bliss — ice bath и сауна в Нимане."),
            (279, "Vibes — сауна, ванны и фитнес."),
            (91, "CNX Sports Recovery — восстановление для спортсменов."),
            (409, "Old City Spa — травяная парная и холодный бассейн."),
            (212, "OUR Space — бассейн и ice bath клуб в Нимане."),
            (476, "Waree Onsen — горячий источник и спа."),
            (256, "Onsen @ Moncham — японский онсен в горах."),
            (89, "Hokka-An — японская дровяная сауна."),
            (209, "Bhura Onsen — минеральные ванны, только для женщин."),
        ],
    },
    {
        "title": "Врачи, которых рекомендуют",
        "description": "Стоматологи, педиатры, ЛОР, глазная клиника, анализы и госпитали — по упоминаниям в чате. Подробности о страховке и ценах — в справочнике.",
        "cover": 168,
        "items": [
            (168, "Стоматология EliteSmile — самая рекомендуемая, англоговорящие врачи."),
            (456, "Prime Dental — стоматология в Чанг Пхыаке."),
            (150, "Empress Dental — стоматология у CMU."),
            (462, "Dental Joy — стоматология на Canal Road."),
            (469, "Стоматологический центр при Ram Hospital."),
            (221, "Dr. Artima — педиатр и семейный врач."),
            (232, "Dr. Pui — педиатр."),
            (361, "ЛОР-клиника Rajvithi."),
            (503, "Глазной госпиталь Saint Peter."),
            (432, "Ma Clinic — дерматолог."),
            (454, "Спортивная клиника и физиотерапия."),
            (435, "HCMC — быстрые медсправки для прав и визы."),
            (424, "Hugsa — анализы и чекапы без очередей."),
            (360, "Ram Hospital — премиум-госпиталь, русскоязычные переводчики."),
            (416, "McCormick — средний ценовой сегмент."),
            (372, "Maharaj (Suan Dok) — главный государственный госпиталь."),
        ],
    },
    {
        "title": "С собакой и кошкой",
        "description": "Ветклиники (включая круглосуточные), передержка и pet-friendly кафе.",
        "cover": 353,
        "items": [
            (353, "Ветеринарный госпиталь при университете — любое оборудование, но очереди."),
            (227, "Zoo Zoo — круглосуточная ветклиника."),
            (188, "Ветгоспиталь в Ханг Донге."),
            (354, "Footprints — клиника в Ханг Донге с высокой оценкой."),
            (404, "Family Pet Clinic на Canal Road."),
            (472, "Chiangmai Animal Hospital."),
            (506, "Sabaidee Pet Clinic."),
            (239, "Royal Cat Hotel — передержка и груминг для кошек."),
            (403, "Mali Cat Cafe."),
            (489, "Elely — кафе со слонами и собаками у реки."),
        ],
    },
    {
        "title": "Глэмпинги и ночёвки в горах",
        "description": "Список из чата: палатки с видом, хоумстеи и кемпинги в 1–2 часах от города — Мон Чам, Самоенг, Мэ Ванг, Чиангдао. Бронируйте заранее на выходные в прохладный сезон (ноябрь–февраль).",
        "cover": "https://maps.app.goo.gl/dQGPa85RVHvuCty97",
        "items": [
            ("https://maps.app.goo.gl/dQGPa85RVHvuCty97", "The Doi Moncham — глэмпинг на Мон Чаме."),
            ("https://maps.app.goo.gl/prGc3i2dS29mcSnv8", "North Star Valley — палатки в долине."),
            ("https://maps.app.goo.gl/YPhFAfM18Rxu1iw4A", "Phu Mork Dao — «гора в тумане»."),
            ("https://maps.app.goo.gl/rBYhV5TsH4Ty1J8f6", "Phu Doi Homestay."),
            ("https://maps.app.goo.gl/eD2jvzfsGrv37bJZ6", "Mon Ing Dao."),
            ("https://maps.app.goo.gl/NBGBx97MyXRbRCpE6", "Chom Khao — кемпинг в Самоенге."),
            ("https://maps.app.goo.gl/yicCyGpFdLFXrg317", "Klin Ai Mok — хоумстей в Самоенге."),
            ("https://maps.app.goo.gl/aLUvJop79toWsi8t5", "Campiness — кемпинг и ферма в Мэ Ванге."),
            ("https://maps.app.goo.gl/FvgYT2XxCXotExbJ6", "3pok Resort — Мэ Ванг."),
            ("https://maps.app.goo.gl/gJKp34Pq3odWk9bJ6", "Wildbeat."),
            ("https://maps.app.goo.gl/3KsYPGabcFPiSeJR8", "Misty Forest."),
            ("https://maps.app.goo.gl/LrmqptYXHbaKHz7v7", "Rhakkao Homestay."),
            ("https://maps.app.goo.gl/tCpFbMpyNGuKrrFo7", "Mt.Cloud — над облаками."),
            ("https://maps.app.goo.gl/HBsaWc7cFZKiDd7F7", "Fine Day."),
            ("https://maps.app.goo.gl/5prB5wMeA1gRTNPV8", "Morning Cloud."),
            ("https://maps.app.goo.gl/KTYUpz5u9g2LjKuG9", "4sky."),
            ("https://maps.app.goo.gl/Kcw3bbiRqebLrgoc7", "Cozy Wild."),
            ("https://maps.app.goo.gl/kUngA1HPb73k415w5", "Lagöm Village Resort."),
            ("https://maps.app.goo.gl/oDbib9YnecS86bgQ9", "Tree House Hideaway — дом на дереве."),
            ("https://maps.app.goo.gl/FBgdW9RiVRKTYki98", "White Bear Camping — Чиангдао."),
            ("https://maps.app.goo.gl/DLwyV1h6UnaQdv128", "The Campian — Чиангдао."),
            ("https://maps.app.goo.gl/eH4djqY374s2jdyt7", "Cocoa Camp."),
            ("https://maps.app.goo.gl/ZehQgSH1mR67RyCh9", "Cocoa Camp Chiang Dao."),
            ("https://maps.app.goo.gl/tDJyLJ4JuSD2Kr5n7", "Din Daeng Doi."),
            ("https://maps.app.goo.gl/RehZWQn2pZEBNgrN6", "Nelamit — Дой Сакет."),
            (178, "Rakkhao — хоумстей и кемпинг на Интаноне."),
            (211, "Baan Ozone — Мон Чам, живая музыка по вечерам."),
            (130, "Amazing Mountain 6 — Мэ Рим."),
            (155, "Take a Walk — дом и ретрит в природе, Дой Сакет."),
        ],
    },
    {
        "title": "Где взять байк или авто",
        "description": "Сводный список прокатов из чата (25+ точек) плюс аренда авто. Никогда не оставляйте паспорт в залог; проверяйте страховку и фотографируйте байк при получении.",
        "cover": "https://maps.app.goo.gl/yt8zYEzdhuxsgHbE6",
        "items": [
            ("https://maps.app.goo.gl/yt8zYEzdhuxsgHbE6", "Cat Motors — самый высокий рейтинг среди прокатов Старого города."),
            ("https://maps.app.goo.gl/9S9NjLw2WVQTpsP58", "TBR Toon's — байки и туры."),
            ("https://maps.app.goo.gl/fn5ChTt5dwCB4bmt6", "Mr Pop — большой выбор."),
            ("https://maps.app.goo.gl/kCQ1pAtb5vYPK2uXA", "Mr. Mechanic №1 — сеть, Ратчапакхинай."), ("https://maps.app.goo.gl/6axA2rGkjrDoapcJA", "Mr. Mechanic №2."), ("https://maps.app.goo.gl/XUJf19QjPjuQBUPC6", "Mr. Mechanic №3."),
            ("https://maps.app.goo.gl/Ynaq3anzEtz3rm1F9", "C&P Big Bikes — большие мотоциклы, Riverside."),
            ("https://maps.app.goo.gl/w5TECByk8SqbLh518", "«Японец» — прокат у Южных ворот, как его называют в чате."),
            ("https://maps.app.goo.gl/KoNLBnqkVv423EAn7", "Joe's Bike Team — Мэ Рим."),
            ("https://maps.app.goo.gl/M6dMyecSKKzTEpub9", "Red Ride — Ханг Донг."),
            ("https://www.google.com/maps/place/M25+Motorbike+rental+CM/@18.7814173,98.989991,3a,75y,90t/data=!3m8!1e2!3m6!1sAF1QipOJYDUU3856uLk1ornOT3PoHbEEtG_UrI6BCU5M!2e10!3e12!6shttps:%2F%2Flh5.googleusercontent.com%2Fp%2FAF1QipOJYDUU3856uLk1ornOT3PoHbEEtG_UrI6BCU5M%3Dw114-h86-k-no!7i2658!8i2000!4m7!3m6!1s0x30da3aa1ea5293db:0x50372924c1938735!8m2!3d18.7815066!4d98.9899939!10e5!16s%2Fg%2F11gcll1nx1", "M25 — Старый город."),
            ("https://maps.app.goo.gl/YC91R95hbAthJLcm9", "Bikky — у Кад Суан Кэу."),
            ("https://maps.app.goo.gl/mvCtZT45zS9sSysb9", "Zippy — Сантитам."),
            ("https://maps.app.goo.gl/Lzzknt5XA5TLz8BC6", "Bamboo Bikes — скутеры и мотоциклы."),
            ("https://maps.app.goo.gl/6aA54SuTGzFTtXKX6", "Buddy's — Ниман."),
            ("https://maps.app.goo.gl/2m9W8WMDuKYpcABm9", "D2 Bike Nimman."), (497, "D2 Bike Changklan — прокат и ремонт."),
            ("https://maps.app.goo.gl/AixzAoVguo81r63S6", "Vanessa's — Чанг Пхыак."),
            ("https://maps.app.goo.gl/ppDMJ9oPe2Nn1tPQ8", "Jeff Bike Rental 200."),
            (375, "Funky Bike."), (378, "Mango Scooter."), (487, "NK Bike — скутеры и велосипеды."),
            (507, "POP Big Bike — туринг и адвенчур."), (433, "Dang Service — биг-байки и туреры."),
            (494, "Chiang Mai Wheels — аренда авто, аэропорт."), (367, "BudgetCatcher — аренда авто."), (502, "POP Service — аренда авто."),
        ],
    },
    {
        "title": "Воркшопы и мастер-классы",
        "description": "Подборка из чата: рисование, керамика, вышивка, украшения из серебра, торты. У каждого места много аналогов — список как карта того, что вообще бывает.",
        "cover": "https://maps.app.goo.gl/wvJWVQR2Cg5Jk5Us5",
        "items": [
            ("https://maps.app.goo.gl/abKnoHPEBnpfP6QLA", "Кафе, где рисуют на мольберте."),
            ("https://maps.app.goo.gl/wvJWVQR2Cg5Jk5Us5", "The Warehouse Paint Club — рисование, лепка, роспись шоперов."),
            ("https://maps.app.goo.gl/rfLVqEpi2etccns66", "Gimmick — украсить торт самим."),
            ("https://maps.app.goo.gl/NdkxgZD1K1pz8eD76", "Aladdin Studio — вышивка ковров и арт-центр."),
            ("https://maps.app.goo.gl/6CbbbTy1eLrXw7mv5", "Mitt Studio — керамика."),
            ("https://maps.app.goo.gl/TkaY68bX2s653j7z6", "Nova Collection — мастер-класс по серебряным украшениям."),
            (94, "Dalha Dalee — крафт и флористика."),
        ],
    },
    {
        "title": "Закаты и виды",
        "description": "Руфтопы, смотровые и озёра, куда ехать за час до заката.",
        "cover": 262,
        "items": [
            (262, "Смотровая Дой Луанг Чиангдао."),
            (343, "Панорамная смотровая Дой Пуй."),
            (428, "Дой Сутеп — храм и вид на город с лестницы нагов."),
            (344, "Озеро CMU — закат над горой Сутеп."),
            (303, "Хуай Тынг Тао — закат с хижины на воде."),
            (78, "MAI Sky Bar в Meliá — самый высокий бар города."),
            (218, "Surr Bar — руфтоп Art Mai Gallery в Нимане."),
            (254, "Salt & Fire — руфтоп в Сантитаме."),
            (104, "See Doi Sky Terrace."),
            (440, "Дамба Мэ Куанг."),
            (498, "«Мост влюблённых» на дамбе Мэ Куанг."),
            (385, "Gramber — кафе на холмах Мэ Рима."),
        ],
    },
    {
        "title": "Тропы и хайкинг",
        "description": "От часовой прогулки к храму в джунглях до кольцевых троп Интанона. Берите воду, выходите рано, в сезон дождей — обувь с протектором.",
        "cover": 315,
        "items": [
            (337, "Тропа монахов к Wat Pha Lat и дальше на Дой Сутеп — 40 минут до храма, 2 часа до вершины."),
            (315, "Wat Pha Lat Hike — вариант того же маршрута."),
            (311, "Тропа Дой Пуй и «облачный пик»."),
            (208, "Каменная тропа на вершину Дой Пуй."),
            (312, "Водопад Монта Тхан и лесная тропа."),
            (195, "Тропы заповедника Чоенг Дой Сутеп."),
            (179, "Кью Мэ Пан — кольцо над облаками, Интанон."),
            (329, "Анг Ка — доисторический облачный лес, Интанон."),
            (320, "Пха Док Сиео — рисовые террасы, Интанон."),
            (338, "Заповедник Чиангдао."),
            (324, "Дой Ланка Ной."),
            (322, "Пху Кханин — гребень Ханг Донг — Самоенг."),
            (318, "Водохранилище Хуай Джо и тропа, Сан Сай."),
            (305, "Он Тай — тёмное небо и тропа Мэ Пха Наен."),
        ],
    },
]


def resolve_ref(conn, ref):
    """Item reference: integer id, or a Google Maps link (stable across DB copies for ingested places)."""
    if isinstance(ref, int):
        return ref
    row = conn.execute("SELECT id FROM items WHERE location_url = ? OR location_url LIKE ? || '?%'", (ref, ref)).fetchone()
    return row[0] if row else None


def upsert(conn, col, kind):
    row = conn.execute("SELECT id FROM collections WHERE title = ?", (col["title"],)).fetchone()
    if row:
        cid = row[0]
        conn.execute("UPDATE collections SET description=?, cover_image=?, duration=?, transport=?, budget=?, kind=? WHERE id=?",
                     (col["description"], cover_path(conn, col.get("cover")), col.get("duration"), col.get("transport"), col.get("budget"), kind, cid))
        conn.execute("DELETE FROM collection_items WHERE collection_id = ?", (cid,))
    else:
        cur = conn.execute("INSERT INTO collections (title, description, cover_image, duration, transport, budget, kind) VALUES (?,?,?,?,?,?,?)",
                           (col["title"], col["description"], cover_path(conn, col.get("cover")), col.get("duration"), col.get("transport"), col.get("budget"), kind))
        cid = cur.lastrowid
    n = 0
    for order, (ref, note) in enumerate(col["items"], 1):
        item_id = resolve_ref(conn, ref)
        if not item_id or not conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone():
            print(f"  ! {col['title']}: item {ref} not found, skipped")
            continue
        conn.execute("INSERT INTO collection_items (collection_id, item_id, sort_order, note) VALUES (?,?,?,?)", (cid, item_id, order, note))
        n += 1
    print(f"  {kind:10s} {col['title']} — {n} items")


def cover_path(conn, item_id):
    """Use the cover item's first photo, if it has one."""
    item_id = resolve_ref(conn, item_id) if item_id else None
    if not item_id:
        return None
    row = conn.execute("SELECT photos_json FROM items WHERE id = ?", (item_id,)).fetchone()
    if row and row[0] and row[0] != "[]":
        import json
        try:
            p = json.loads(row[0])
            if p:
                return p[0].lstrip("/")
        except Exception:
            pass
    import os
    return f"static/photos/places/{item_id}.jpg" if os.path.exists(f"static/photos/places/{item_id}.jpg") else None


def main():
    conn = sqlite3.connect(DB)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(collections)")}
    if "kind" not in cols:
        conn.execute("ALTER TABLE collections ADD COLUMN kind TEXT DEFAULT 'route'")
    for c in ROUTES:
        upsert(conn, c, "route")
    for c in COLLECTIONS:
        upsert(conn, c, "collection")
    conn.commit()
    print("Total collections:", conn.execute("SELECT count(*) FROM collections").fetchone()[0])


if __name__ == "__main__":
    main()
