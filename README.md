# Чиангмай — гид сообщества

> Места, события, маршруты и справочник по Чиангмаю, собранные из русскоязычных Telegram-чатов.

🌐 **Live:** [https://artartemev.github.io/chiangmai-guide/](https://artartemev.github.io/chiangmai-guide/)

---

## Архитектура

Статический сайт (GitHub Pages) поверх экспортированного JSON + локальный Python-хаб для курации данных.

```
chiangmai_guide.db        мастер-база (SQLite): items, reviews, collections, collection_items
├─ export_static.py       DB → static/data.json (места, коллекции, статистика) + static/reviews.json (цитаты)
├─ geocode.py             обогащение мест из ссылок Google Maps: координаты, телефон, сайт, рейтинг, часы
├─ ingest_lists.py        добавление мест из списков чата (название + ссылка на карту)
├─ seed_collections.py    маршруты и подборки (редактируются прямо в файле)
├─ update_wiki.py         статьи справочника → static/wiki.json
└─ app.py                 FastAPI для локальной работы с базой (опционально)

index.html                разметка
static/css/app.css        стили (светлая/тёмная тема по системной настройке)
static/js/app.js          приложение: роутинг, фильтры, карта, карточки
static/wiki.json          справочник (markdown в JSON)
```

Фронтенд — без фреймворков: Leaflet + OpenStreetMap для карты, `marked` для статей. Роутинг по хэшу, поэтому любой экран можно скинуть ссылкой: `#/place/60`, `#/map?cat=nature`, `#/routes/7`, `#/wiki/visas`, `#/events`.

## Обновление данных

```bash
# 1. Добавили/поправили места в базе → обогатить новые ссылки на карты
python3 geocode.py            # только места без координат; --all чтобы обновить рейтинги и часы у всех

# 2. Пересобрать маршруты/подборки и справочник (если менялись)
python3 seed_collections.py
python3 update_wiki.py

# 3. Экспорт и публикация
python3 export_static.py
git add static/data.json static/reviews.json static/wiki.json chiangmai_guide.db
git commit -m "Update catalog data"
git push
```

## Добавление мест из списков чата

Когда в чате появляется список «название — ссылка на Google Maps» (прокаты, глэмпинги, воркшопы):

```bash
python3 ingest_lists.py lists.json   # формат: {"key": {"msg": id, "date": ..., "from": ..., "items": [["заметка", "url"], ...]}}
```

Категория и вводный текст для каждого `key` задаются в `LIST_META` внутри скрипта. Место получает координаты, официальное название, рейтинг, телефон и часы работы из Google, а в `reviews` записывается ссылка на исходное сообщение.

## Локальный запуск

```bash
python3 -m http.server 8090      # статика, откройте http://localhost:8090
```

или с API поверх базы:

```bash
pip install -r requirements.txt
python3 app.py                   # http://localhost:8080
```

## Админка (локально)

Правки и удаление мест — прямо на сайте, без правки Python:

```bash
python3 app.py                   # http://localhost:8080
```

Когда сайт открыт с localhost и `app.py` отвечает, включается режим админа:

- на карточках мест и событий при наведении — 🗑 «Скрыть» (с «Отменить» в тосте);
- в панели места — «Изменить» (название, категория, район, описание, теги, ссылки, телефон, veg) и «Скрыть»;
- в шапке — «Опубликовать»: экспорт `data.json` + `git commit` + `git push` (точка на кнопке = есть неопубликованное).

Каждое действие сразу пишется в базу, в `data/curation.json` и переэкспортируется в `static/data.json`. `curation.json` — источник правды для ручных правок: `export_static.py` и `apply_updates.py` применяют его поверх всего, что насчитали скрипты (`tag_items.py`, геокодер), поэтому ежедневный сбор их не перетирает. В файл попадают только изменённые поля.

API отвечает только с 127.0.0.1; на GitHub Pages ничего из этого не видно.

## Как устроен геокодер

Ссылка `maps.app.goo.gl/…` редиректит на `maps.google.com/?q=…&ftid=<id>`. По `cid` (вторая половина `ftid`) эндпоинт `maps.google.com/maps?cid=…&output=embed` отдаёт HTML с точными координатами, рейтингом, телефоном, сайтом и часами — без API-ключа. Результат принимается только если `ftid` совпал, поэтому чужие заведения не подмешиваются.
