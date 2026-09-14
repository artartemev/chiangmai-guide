# CHIANG MAI // AI FIELD GUIDE [TE-01]

> Нишевый интерактивный каталог мест, коворкингов, клиник, маршрутов и событий Чиангмая на базе Telegram-сообщества в эстетике Teenage Engineering.

🌐 **Live Demo:** [https://artartemev.github.io/chiangmai-guide/](https://artartemev.github.io/chiangmai-guide/)

---

## Архитектура
Проект работает в гибридном режиме:
1. **Static Jamstack (GitHub Pages):** Фронтенд (`index.html`) читает скомпилированный `static/data.json` и `static/wiki.json`, обеспечивая мгновенную фильтрацию, поиск и работу без серверов.
2. **Local Python Hub (FastAPI + SQLite):** Мастер-база `chiangmai_guide.db` для парсинга чатов, курации и обогащения данных.

---

## Обновление данных для продакшна

Когда база `chiangmai_guide.db` обновлена (добавлены новые места или спарсены новые события):

```bash
# 1. Экспортировать базу в статический data.json
python3 export_static.py

# 2. Запушить изменения на GitHub (сайт обновится за 30 секунд)
git add static/data.json index.html
git commit -m "Update catalog data"
git push
```

## Локальный запуск сервера (опционально)
```bash
pip install fastapi uvicorn
python3 app.py
```
Сервер будет доступен по адресу `http://localhost:8080`.
