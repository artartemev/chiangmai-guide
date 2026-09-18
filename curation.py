"""
Manual curation store: data/curation.json.

Every edit or archive made through the local admin (app.py) is written here so it
survives the daily pipeline, which may re-tag items or re-run export. `apply()` is
called from export_static.py and apply_updates.py, so the file always wins over
what the scripts computed. Keys are item ids — they are autoincrement and never reused.
"""
import json
import os
from datetime import datetime

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "curation.json")
EDITABLE = {"title", "category", "neighborhood", "description", "tags", "veg_friendly", "location_url",
            "website", "phone_contact", "event_date", "event_iso_date", "venue_name", "address"}


def load():
    try:
        with open(PATH, encoding="utf-8") as f:
            d = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        d = {}
    d.setdefault("archived", {})
    d.setdefault("edits", {})
    return d


def save(d):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, PATH)


def record_edit(item_id, fields, title=None):
    d = load()
    e = d["edits"].setdefault(str(item_id), {})
    e.update({k: v for k, v in fields.items() if k in EDITABLE})
    e["_title"] = title or e.get("_title") or fields.get("title", "")
    e["_at"] = datetime.now().isoformat(timespec="seconds")
    save(d)


def record_archive(item_id, title, archived=True):
    d = load()
    if archived:
        d["archived"][str(item_id)] = {"title": title, "at": datetime.now().isoformat(timespec="seconds")}
    else:
        d["archived"].pop(str(item_id), None)
    save(d)


def apply(conn):
    """Re-apply stored curation to the DB. Safe to run any number of times."""
    d = load()
    n = 0
    for iid, fields in d["edits"].items():
        cols = {k: v for k, v in fields.items() if k in EDITABLE}
        if not cols:
            continue
        if "tags" in cols and not isinstance(cols["tags"], str):
            cols["tags"] = json.dumps(cols["tags"], ensure_ascii=False)
        if "veg_friendly" in cols:
            cols["veg_friendly"] = 1 if cols["veg_friendly"] else 0
        sets = ", ".join(f"{k}=?" for k in cols)
        n += conn.execute(f"UPDATE items SET {sets} WHERE id=?", (*cols.values(), int(iid))).rowcount
    ids = [int(i) for i in d["archived"]]
    if ids:
        conn.execute(f"UPDATE items SET status='archived' WHERE id IN ({','.join('?' * len(ids))})", ids)
    conn.commit()
    return n, len(ids)
